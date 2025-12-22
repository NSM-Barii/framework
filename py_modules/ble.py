# TEST MODULE WILL BE STARTING BLE FRAMEWORK FROM HERE


# UI IMPORTS
from rich.console import Console


# HACKING IMPORTS
from bleak import BleakClient, BleakScanner


# ETC IMPORTS
import asyncio

console = Console()



class BLE_Sniffer():
    """This will be a ble hacking framework"""



    @classmethod
    async def _ble_discover(cls, timeout):
        """This will sniff traffic"""


        devices =  await BleakScanner.discover(timeout=timeout, return_adv=True)

        return devices
    


    @classmethod
    def _ble_printer(cls, timeout):
        """Lets enumerate"""


        c1 = "bold red"
        c2 = "bold yellow"
        c3 = "bold green"
        c4 = "bold red"
        c5 = "bold blue"


        try:

            devices = asyncio.run(BLE_Sniffer._ble_discover(timeout=timeout))
            
            if not devices: return

            
            
            for mac, (device, adv) in devices.items():

                if mac not in cls.devices:


                    name = adv.local_name or False
                    rssi = adv.rssi
                    uuid = adv.service_uuids or False
                    manuf = adv.manufacturer_data


                    data = {
                        "addr": mac,
                        "rssi": rssi,
                        "name": name,
                        "manuf": manuf,
                        "uuid": uuid
                    }

                    cls.devices.append(mac)
                    cls.data[mac] = data

                    p1 = c3
                    p2 = "white"



                    console.print(f"[{c3}][+][/{c3}] [{p1}]Addr:[{p2}] {mac} - [{p1}]RSSI:[{p2}] {rssi} - [{p1}]Local_name:[{p2}] {name} - [{p1}]Manufacturer:[{p2}] {manuf} - [{p1}]UUID:[{p2}] {uuid}")
            

        except Exception as e:
            console.print(f"[bold red]Sniffer Exception Error:[bold yellow] {e}")



        
    @classmethod
    def main(cls, timeout=2):
        """Run from here"""

        cls.devices = []
        cls.data = {}

        i = 3
        while i > 0:
            BLE_Sniffer._ble_printer(timeout=timeout); i -= 1
        
        #console.print(cls.devices)

        for mac in cls.devices:

            if mac == "CC:38:35:30:6F:83": return mac, cls.data[mac]




class BLE_Connector():
    """This class will be responsible for performing connections --> BLE"""



    @classmethod
    async def _get_chars(cls, client, uuid=False):
        """This method will be responsible for pulling chars"""


        chars = await client.read_gatt_char(char_specifier=uuid)


    @classmethod
    def _connector(cls, target, uuid):
        """This will be responsible for performing connection --> Client"""



        client = BleakClient(address_or_ble_device=target)

        client.connect()

        chars = asyncio.run(BLE_Connector._get_chars(client=client, uuid=uuid))

        console.print(client, chars)
    

    @classmethod
    def main(cls, target, data):
        """This will run class methods"""


        uuid = data["uuid"]
        BLE_Connector._connector(target=target, uuid=uuid)


        
if __name__ == "__main__":
    target, data = BLE_Sniffer.main()
    BLE_Connector.main(target=target, data=data)