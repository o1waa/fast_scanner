import socket
import argparse
import time
from concurrent.futures import ThreadPoolExecutor

def scan_port(target, port, open_ports):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5) 
            if sock.connect_ex((target, port)) == 0:
                try:
                    service = socket.getservbyport(port, "tcp")
                except OSError:
                    service = "unknown"

                print(f"[+] Port {port:<5}/tcp | Služba: {service}")
                open_ports.append((port, service))
    except OSError:
        pass

def parse_ports(port_str):
    ports = []
    if "-" in port_str:
        start, end = map(int, port_str.split("-"))
        ports = list(range(start, end + 1))
    elif "," in port_str:
        ports = [int(p.strip()) for p in port_str.split(",")]
    else:
        ports = [int(port_str)]
    return ports

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrémně rychlý Python Port Scanner")
    parser.add_argument("-t", "--target", required=True, help="Cílová IP adresa nebo doména")
    parser.add_argument("-p", "--ports", default="1-1024", help="Rozsah portů (např. '1-1024' nebo '1-65535')")
    parser.add_argument("-w", "--workers", type=int, default=500, help="Počet vláken (default: 500 pro max rychlost)")
    parser.add_argument("-o", "--output", help="Soubor pro uložení výsledků")
    
    args = parser.parse_args()

    target_clean = args.target.replace("https://", "").replace("http://", "").split('/')[0]

    try:
        target_ip = socket.gethostbyname(target_clean)
    except socket.gaierror:
        print(f"[-] Chyba: Nelze přeložit doménu '{args.target}'.")
        exit()

    ports_to_scan = parse_ports(args.ports)
    open_ports = []

    print("=" * 60)
    print(f" Bleskový sken: {target_clean} ({target_ip})")
    print(f" Portů: {len(ports_to_scan)} | Vláken: {args.workers}")
    print("=" * 60 + "\n")

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for port in ports_to_scan:
            executor.submit(scan_port, target_ip, port, open_ports)

    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)

    print("\n" + "=" * 60)
    print(f"[+] Hotovo za {elapsed_time} sekund!")
    print(f"[+] Otevřených portů: {len(open_ports)} z {len(ports_to_scan)}")
    print("=" * 60)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(f"Výsledky skenování pro {target_clean} ({target_ip})\n")
            f.write(f"Čas trvání: {elapsed_time} s\n\n")
            for item in sorted(open_ports, key=lambda x: x[0]):
                f.write(f"Port {item[0]}/tcp - {item[1]}\n")
        print(f"[+] Výsledky zapsány do: {args.output}")