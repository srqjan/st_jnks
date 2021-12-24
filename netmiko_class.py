from netmiko import ConnectHandler


class Device(object):
    def __init__(self):
        self.ip = "192.168.128.2"
        self.username = "admin"
        self.password = "password"
        self.device_type = 'eltex'
        self.connect

    # Method that connects to device when class is initialized
    @property
    def connect(self):
        return ConnectHandler(ip=self.ip, device_type=self.device_type,
                              username=self.username, password=self.password)
    
    # Method that calls DeviceInfo Class and returns atrributes
    def get_device_info(self):
        return DeviceInfo(self.connect)
 
class DeviceInfo(object):
    def __init__(self, conn):
        self.conn = conn
        self.get_info
    
    # Method that gathers data and assigns attributes to __init__
    @property
    def get_info(self):
        result = self.conn.send_command("show version")
        for key in result[0]:
            setattr(self, key, result[0][key])


if __name__ == "__main__":
    device = Device()
    results = device.get_device_info()
    print(results.version)
    print(results.hostname)
    print(results.serial)
    print(results.uptime)
    print(results.config_register)
