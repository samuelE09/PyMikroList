#Importamos las librerias necesarias

import time
import configparser
import ros_api
import paramiko
import pandas as pd
from prettytable import PrettyTable

#Creamos un objeto el cual contendra las conexiones a las dos librerias  (ros_api , paramiko)
class Router():
    #Inicializamos los valores que tendra nuestra conexión
    def __init__(self, Direccion_IP, Username, Password, Puerto):
        self.Direccion_IP = Direccion_IP
        self.Username = Username
        self.Password = Password
        self.Puerto = Puerto
    
    #Inicializamos la conexion con ros_api y retornamos la conexión
    def conexion_ros_api(self):
        router = ros_api.Api(
            f'{self.Direccion_IP}', 
            user=f'{self.Username}', 
            password=f'{self.Password}', 
            port=self.Puerto)

        return router
    
    #Inicializamos la conexion con paramiko y retornamos la conexión
    def conexion_paramiko(self):
        router = paramiko.SSHClient()
        router.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        router.connect(f"{self.Direccion_IP}", username=f"{self.Username}", password=f"{self.Password}")
        
        return router

#Definimos el banner de nuestro programa   
def banner_program():
  
  import pyfiglet

  # Heading
  banner = pyfiglet.figlet_format("PyMikroList", font="big")

  # List of Content
  info_lines = [
    "  [+] Program: PyMikroList",
    "  [+] Description: Script to list Move IP addresses between Address List",
    "  [+] Version: 0.1.0",
    "  [+] Author: Samuel E. Berru",
    "  [+] Github: https://github.com/samuelE09/PyMikrolist",
  ]

  # Variables
  width = max(len(line) for line in info_lines)
  square_top = "+" + "=" * width + "+"
  square_bottom = "+" + "=" * width + "+"

  # Banner Centering
  banner_lines = banner.split("\n")
  centered_banner_lines = [line.center(width) for line in banner_lines]
  centered_banner = "\n".join(centered_banner_lines)

  info_lines = [line.ljust(width) for line in info_lines]

  print(square_top)
  print(centered_banner)
  for line in info_lines:
    print(line)
  print(square_bottom)

#creamos el menu de opciones-funcionalidades que tendrá el script 
def menu_program():

  from prettytable import PrettyTable

  options = {"1":"All Address Lists",
            "2":"Move IP Addresses",
            "3": "Exit"}

  table = PrettyTable()
  # Añade las columnas de índice y list
  table.add_column("Option", [key for key in options.keys()])
  table.add_column("Operation", [value.ljust(len(value)) for value in options.values()])

  print(table)

  option_selected = input("\n [*] Select an option: ")

  return options, option_selected

#obtenemos el archivo, leemos y extraemos los datos (direcciones IP)
def read_file(file):
    
    try:
        #Lectura del Archivo Excel 
        data = pd.read_excel(f"{file}")
        info = pd.DataFrame(data)
        info = info["Dirección IP"]
        msg = "Successful Reading"
        
    except:
        info = []
        msg = "Could not read file"

    return info, msg

#Pasamos el objeto router que lleva la conexión y ejecutamos los comandos para obtener las Address List del Equipo 
def all_address_list(router):
    
    #Establecemos la conexion con la libreria y obtenemos las Address List
    try:
        r = router.talk('/ip/firewall/address-list/print')  
        list_count = {}
        for item in r:
            if item["list"] not in list_count:
                list_count[item["list"]] = 1
            else:
                list_count[item["list"]] += 1
        table = PrettyTable()
        # Añade las columnas de índice y list
        table.add_column("#", range(1, len(list_count) + 1))
        table.add_column("List", [key for key in list_count.keys()])
        table.add_column("IP Addresses", [value for value in list_count.values()])
        
        return list_count, table , "Connection established"
    
    except:  
        r = [] 
        return r , "Connection not established"

#Pasamos el objeto router que lleva la conexión y ejecutamos los comandos para mover las direcciones IP, de un Address List a Otro, del Equipo 
def operation_IP(router, to_lista, file):
    #obtenemos la lista de direcciones IP's
    info , msg = read_file(file)
    
    #Establecemos la conexion con la libreria y ejecutamos los comandos para remover y agregar las direcciones IP
    try:
        if len(info) != 0:
            for ip in info:
                stdin, stdout, stderr = router.exec_command(
                    f'/ip firewall address-list remove [find address="{ip}"]')
                stdin, stdout, stderr = router.exec_command(
                    f'/ip firewall address-list add address={ip} list="{to_lista}"')
                time.sleep(1)

            msg = "Moved Succesfull"
        else:  
            msg = "There is nothing to move"
        
        router.close() 
        return msg
    
    except:  
        
        return "Connection not established"


if __name__ == "__main__":
    
    try:
        
        #Accedemos a los parametros de nuestro equipo 
        config = configparser.ConfigParser()
        config.read('settings.ini')
        ip = config.get("configuracion", "direccion_ip")
        user = config.get("configuracion", "usuario")
        pwd = config.get("configuracion", "pass")
        port = config.get("configuracion", "puerto")
        file = config.get("configuracion", "nom_archivo")
        
        banner_program()
        
        #Iniciamos el programa 
        options, option_selected = menu_program()
        r1 = Router(ip,user,pwd,port)
        
        if option_selected in options:
            
            if option_selected == "1":
                data, respuesta, msg = all_address_list(r1.conexion_ros_api())
                print(f"\n {msg}")
                print(f"\n {respuesta}")
                
            elif option_selected == "2":
                
                data, table_all, msg = all_address_list(r1.conexion_ros_api())
                opciones  = [ item for item in data.keys()]

                table = PrettyTable()
                # Añade las columnas de índice y list
                table.add_column("#", range(1, len(data) + 1))
                table.add_column("List", [key for key in data.keys()])
                print(f"\n {table}")
                
                while True: 
                    
                    opcion = int(input("\n [*] To which list do you want to move the IPs: "))
                        
                    if opcion in range(1, len(opciones)+1):
                        lista_seleccionada = opciones[opcion-1]
                        msg = operation_IP(r1.conexion_paramiko(),lista_seleccionada, file)
                        print(f"\n {msg}")
                        break
                    else:
                        print("\n [Warning!] Invalid option. Please select a valid option.")
                        
            elif option_selected == "3":
                print(f"\nExiting the Program ......! ")
                time.sleep(3)
                exit()
        else: 
            print("\n [Warning!] Run the program again and select a valid option.")
            
    except KeyboardInterrupt:
        print("\n Program interrupted by the user. Exiting.....!")
        time.sleep(3)
        exit()
    
    except Exception as err:
        print(f"\n Unexpected {err=}, {type(err)=}")   

    