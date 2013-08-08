# MULTICAST

def get_total_streaming_clients(output):
    for line in output:
        if line.startswith("TOTAL: "):
            return int(line.split(" ")[1])

conf.add(Subprocess(
    name="selfstreaming clients multicast",
    cmd="~sebastiann/iptvstats.py",
    func=get_total_streaming_clients
))



# UNICAST

def format_int(output):
    return int(output[0])

conf.add(Subprocess(
    name="selfstreaming clients unicast",
    cmd="curl stream.selfnet.de/proxy/status/ 2>/dev/null | grep -B 2 '</table>' | grep '    <td>' | cut -d '>' -f 2 | cut -d '<' -f 1",
    func=format_int
))

