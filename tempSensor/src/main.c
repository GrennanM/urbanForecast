// Very basic DS18B20 implementation
//
// !!! NOT YET TESTED WITH A REAL DS18B20 !!!
//
// Refer https://github.com/feelfreelinux/ds18b20/blob/master/ds18b20.c
//   and https://datasheets.maximintegrated.com/en/ds/DS18B20.pdf
//   and https://www.maximintegrated.com/en/app-notes/index.mvp/id/126
//   and https://github.com/milesburton/Arduino-Temperature-Control-Library
//

#include <zephyr.h>
#include <board.h>
#include <device.h>
#include <gpio.h>
#include <irq.h>
#include <misc/printk.h>

#define PORT	"GPIO_0"
#define PIN		11
#define SLEEP_TIME 5000

// // LED setup
#define LED_PORT LED0_GPIO_CONTROLLER
#define LED	LED0_GPIO_PIN
#define TEMP_THRESHOLD 24

struct device *dev;
struct device *dev1; //for LED
//
// NOTE: Assumes a DS18B20 with a 4.7Kohm resistor between DATA and Vcc pins.
// NOTE: Not assuming parasitic power supply to DS18B20.
//
// NOTE: We use irq_lock and irq_unlock below to temperarily disable interrupts
//       (and hence multithreading) while we pause for very short delays to
//       implement 1-wire protocol timings.
//

// Send one bit over 1-wire
void ds18b20_send_bit(u8_t bit)
{
	unsigned int key;

	if (bit == 1) {
		// Send a 1
		key = irq_lock();
		gpio_pin_configure(dev, PIN, GPIO_DIR_OUT);
		gpio_pin_write(dev, PIN, 0);
		k_busy_wait(5); // 5
		gpio_pin_write(dev, PIN, 1);
		irq_unlock(key);
		k_busy_wait(85); // 80
	} else {
		// Send a 0
		key = irq_lock();
		gpio_pin_configure(dev, PIN, GPIO_DIR_OUT);
		gpio_pin_write(dev, PIN, 0);
		k_busy_wait(85); // 85
		gpio_pin_write(dev, PIN, 1);
		irq_unlock(key);
		k_busy_wait(5); // 0
	}
}

// Receive one bit over 1-wire
u8_t ds18b20_recv_bit(void)
{
	u32_t value = 0;
	unsigned int key;

	key = irq_lock();
	gpio_pin_configure(dev, PIN, GPIO_DIR_OUT);
	gpio_pin_write(dev, PIN, 0);
	k_busy_wait(3);
	gpio_pin_write(dev, PIN, 1);
	k_busy_wait(15); // 15
	gpio_pin_configure(dev, PIN, GPIO_DIR_IN);
	gpio_pin_read(dev, PIN, &value);
	irq_unlock(key);
	k_busy_wait(53); // 15

	return value & 0x01;
}

// Send one byte over 1-wire
void ds18b20_send_byte(u8_t data)
{
	u8_t i;
    u8_t x;


    for(i = 0; i < 8; i++){
		x = data >> i;
		x &= 0x01;
		ds18b20_send_bit(x);
    }

	// Wait between bytes
	k_busy_wait(100);
}

// Receive one byte over 1-wire
u8_t ds18b20_recv_byte(void)
{
	u32_t i;
    u8_t data = 0;

    for (i = 0; i < 8; i++) {
      	if(ds18b20_recv_bit()) {
	  		data |= (0x01 << i);
		}
	}

    return(data);
}

// Send 1-wire reset pulse
u8_t ds18b20_reset_pulse()
{
	u32_t value = 0;
	u32_t result = 0;
	unsigned int key;

	key = irq_lock();
	gpio_pin_configure(dev, PIN, GPIO_DIR_OUT);
	gpio_pin_write(dev, PIN, 0);
	k_busy_wait(480);
	gpio_pin_configure(dev, PIN, GPIO_DIR_IN);
	k_busy_wait(70);
	gpio_pin_read(dev, PIN, &value);
	result = value == 0 ? 1 : 0;
	irq_unlock(key);
	k_busy_wait(410);

	return result;
}

// Trigger a DS18B20 temperature measurement and receive the result over 1-wire
s16_t ds18b20_get_temp()
{
	u8_t check;
    u8_t tempMSB=0;
	u8_t tempLSB=0;

    check=ds18b20_reset_pulse();

    if(check==0) {
		printk("Device not detected\n");
		return 0;
	}

	// Trigger conversion
	ds18b20_send_byte(0xCC);
	ds18b20_send_byte(0x44);

	// It takes up to 750 ms for a conversion to complete at maximum resolution
	k_sleep(750);

	check=ds18b20_reset_pulse();

    if(check==0) {
		printk("Device not detected\n");
		return 0;
	}

	// Send read command
	ds18b20_send_byte(0xCC);
	ds18b20_send_byte(0xBE);

	// Read bytes sent by DS18B20
	tempLSB=ds18b20_recv_byte();
	tempMSB=ds18b20_recv_byte();

	check=ds18b20_reset_pulse();

	if(check==0) {
		printk("Device not detected\n");
		return 0;
	}

	// Convert to degrees C temperature, dropping everything to the right
	// of the decimal point (NOTE: you might want to retain this additional
	// accuracy and add FP support to publish FP data to thingsboard.io!!)
	return (s16_t)((((u16_t)tempMSB << 8) + (u16_t)tempLSB) >> 4);
}

void main(void)
{
	u16_t temperature;

	// LED setup
	printk("Starting...\n");
	dev1 = device_get_binding(LED_PORT); // get binding for LED
	gpio_pin_configure(dev1, LED, GPIO_DIR_OUT); // configure LED

	// temperature
	printk("Preparing DS18B20\n");
	dev = device_get_binding(PORT);

	if (gpio_pin_configure(dev, PIN, GPIO_DIR_IN)) {
		printk("Pin configure failed\n");
	}

	while (true) {

		// delay between samples
		k_sleep(SLEEP_TIME);

		printk("\nSampling ... ");

		temperature = ds18b20_get_temp();

		// LED setup: turn on/off LED depending on temperature
		if (temperature > TEMP_THRESHOLD){
			gpio_pin_write(dev1, LED, 0); //turn on
		}
		else{
			gpio_pin_write(dev1, LED, 1); // turn off
		}

		printk("current temperature: %i degrees C\n", temperature);

	}
}
