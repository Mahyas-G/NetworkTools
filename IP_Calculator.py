import ipaddress

def get_ip_class(ip):
    first = int(str(ip).split('.')[0])
    if first < 128:   return 'A'
    if first < 192:   return 'B'
    if first < 224:   return 'C'
    if first < 240:   return 'D (Multicast)'
    return 'E (Reserved)'

def is_private(ip):
    return ipaddress.ip_address(ip).is_private

def to_binary(ip):
    return '.'.join(f'{int(o):08b}' for o in str(ip).split('.'))

def ip_calculator(cidr):
    network = ipaddress.ip_network(cidr, strict=False)
    prefix = network.prefixlen
    total = network.num_addresses

    if prefix == 32:
        usable = 1
        first_host = last_host = network.network_address
    elif prefix == 31:
        usable = 2
        first_host = network.network_address
        last_host  = network.broadcast_address
    else:
        usable = total - 2
        first_host = network.network_address + 1
        last_host  = network.broadcast_address - 1

    return {
        "cidr":          f"{network.network_address}/{prefix}",
        "network":       network.network_address,
        "broadcast":     network.broadcast_address,
        "subnet_mask":   network.netmask,
        "wildcard_mask": network.hostmask,
        "first_host":    first_host,
        "last_host":     last_host,
        "total":         total,
        "usable_hosts":  usable,
        "ip_class":      get_ip_class(network.network_address),
        "private":       is_private(network.network_address),
        "bin_network":   to_binary(network.network_address),
        "bin_mask":      to_binary(network.netmask),
        "bin_wildcard":  to_binary(network.hostmask),
    }

def print_result(r):
    width = 22
    print("\n" + "=" * 50)
    print(f"  IP Subnet Calculator")
    print("=" * 50)
    print(f"  {'CIDR Notation':<{width}} {r['cidr']}")
    print(f"  {'Network Address':<{width}} {r['network']}")
    print(f"  {'Broadcast Address':<{width}} {r['broadcast']}")
    print(f"  {'Subnet Mask':<{width}} {r['subnet_mask']}")
    print(f"  {'Wildcard Mask':<{width}} {r['wildcard_mask']}")
    print(f"  {'First Usable Host':<{width}} {r['first_host']}")
    print(f"  {'Last Usable Host':<{width}} {r['last_host']}")
    print(f"  {'Total Addresses':<{width}} {r['total']:,}")
    print(f"  {'Usable Hosts':<{width}} {r['usable_hosts']:,}")
    print(f"  {'IP Class':<{width}} {r['ip_class']}")
    print(f"  {'Private Range':<{width}} {'Yes (RFC 1918)' if r['private'] else 'No'}")
    print("-" * 50)
    print(f"  Binary Representation")
    print(f"  {'Network':<{width}} {r['bin_network']}")
    print(f"  {'Subnet Mask':<{width}} {r['bin_mask']}")
    print(f"  {'Wildcard Mask':<{width}} {r['bin_wildcard']}")
    print("=" * 50 + "\n")

while True:
    raw = input("Enter IP/CIDR (or 'q' to quit): ").strip()
    if raw.lower() == 'q':
        break
    try:
        print_result(ip_calculator(raw))
    except ValueError:
        print("  [Error] Invalid IP/CIDR format. Try again.\n")
