import configparser
import ros_api

class Router():
    def __init__(self, Direccion_IP, Username, Password, Puerto):
        self.Direccion_IP = Direccion_IP
        self.Username = Username
        self.Password = Password
        self.Puerto = Puerto
        
    def conexion_ros_api(self):
        router = ros_api.Api(
            f'{self.Direccion_IP}', 
            user=f'{self.Username}', 
            password=f'{self.Password}', 
            port=self.Puerto)
        
        return router
     
def all_address_list(router):
    from prettytable import PrettyTable
    #Establecemos la conexion con la libreria
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
        table.add_column("Direcciones IP", [value for value in list_count.values()])
        
        return table , "Conexion Establecida"
    except:  
        r = [] 
        return r , "Conexion no Establecida"
    
    
def operation_IP():
  return "Opcion 2 Seleccionada"


if __name__ == "__main__":
    print("Bienvenidos")
    
    opciones = {"1":"Address List Firewall",
                "2":"Agregar IP a Address List",
                "3":"Mover Ip a Otra Address List",
                "4":"Salir"}
    print('\n'.join(f"{id}:{valor}" for id, valor in opciones.items()))
    
    #obtenemos los parametros de la conexion 
    config = configparser.ConfigParser()
    config.read('settings.ini')
    ip = config.get("configuracion", "direccion_ip")
    user = config.get("configuracion", "usuario")
    pwd = config.get("configuracion", "pass")
    port = config.get("configuracion", "puerto")
    
    option_selected = input("\n [*] Select an option: ")
    
    if option_selected in opciones:
        if option_selected == "1":
            r1 = Router(ip,user,pwd,port)
            respuesta, msg = all_address_list(r1.conexion_ros_api())
            print(msg)
            print(respuesta)
        else:
            print("Termino el Programa")