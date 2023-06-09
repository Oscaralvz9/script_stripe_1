import time
import stripe
from proxmoxer import ProxmoxAPI
import random
import string

stripe.api_key = "sk_test_51NDUj6DNPLz8JxRFXc8qsQqNPpyEA2gIsipK2byY81OCQyfZxtKXLYz4xnxwH0MaULLKIneWDevceNB74DexWOu300F0tz2gm3"

proxmox = ProxmoxAPI("vidal99.softether.net", user="api@pve", password="password", verify_ssl=False)

def generate_container_id():
    return random.randint(100, 999)

def generate_container_name():
    prefix = "container_"
    suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
    return prefix + suffix

vm_node = "node1"
vm_os = "local:vztmpl/debian-11-turnkey-lamp_17.1-1_amd64.tar.gz"

def create_container():
    vm_id = generate_container_id()
    vm_name = generate_container_name()

    proxmox.nodes(vm_node).lxc.create(
        vmid=vm_id,
        ostemplate=vm_os,
        password="admin",
        net0="name=eth0,bridge=vmbr0,ip=dhcp",
        storage="local-lvm",
        memory=512,
        cores=1,
        start=1
    )

    print(f"Contenedor '{vm_name}' con ID '{vm_id}' creado exitosamente en el nodo '{vm_node}'.")

def leer_ultimo_pago():
    with open("ultimo_pago.txt", "r") as file:
        return file.read().strip()

def escribir_ultimo_pago(pago_id):
    with open("ultimo_pago.txt", "w") as file:
        file.write(pago_id)

while True:
    ultimo_pago_guardado = leer_ultimo_pago()

    payment_intents = stripe.PaymentIntent.list(
        limit=1,
        expand=['data.customer']
    )

    if len(payment_intents.data) > 0:
        ultimo_pago = payment_intents.data[0]
        pago_id = ultimo_pago.id

        if pago_id != ultimo_pago_guardado:
            escribir_ultimo_pago(pago_id)

            create_container()

            print("Ejecutando el script con el ID del pago:", pago_id)
    else:
        print("No se encontraron pagos.")

    time.sleep(1)