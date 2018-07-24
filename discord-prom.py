import discord, re, requests, os, time

TOKEN = 'NDcxMDU4MzY2NDk2NTA1ODY3.DjfS9Q.j0HzLYIrzgbFJOfFtTWJnA3Tnso'

client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if 'memory' in message.content.lower() and "use" in message.content.lower():
        usage_val = usage('memory', message)
        val = sizeFormat(usage_val)
        msg = "{0} in use right now!".format(val)
        await client.send_message(message.channel, msg)
    elif 'storage' in message.content.lower() and "use" in message.content.lower():
        usage_val = usage('storage', message)
        val = sizeFormat(usage_val)
        msg = "{0} in use right now!".format(val)
        await client.send_message(message.channel, msg)
    elif 'monitor' in message.content.lower():
        counter = 0
        if 'rx' in message.content.lower():
            await client.send_message(message.channel, "probing...")
            host = findHost(message)
            stat = "node_network_receive_bytes"
            for each in getRate(stat, host):
                await client.send_message(message.channel, each)
                time.sleep(1)
        elif 'tx' in message.content.lower():
            await client.send_message(message.channel, "probing...")
            host = findHost(message)
            stat = "node_network_transmit_bytes"
            for each in getRate(stat, host):
                await client.send_message(message.channel, each)
                time.sleep(1)
        elif 'read' in message.content.lower():
            await client.send_message(message.channel, "probing...")
            host = findHost(message)
            stat = 'node_disk_bytes_read{device="sda"}'
            for each in getRate(stat, host):
                await client.send_message(message.channel, each)
                time.sleep(1)
        elif 'write' in message.content.lower():
            await client.send_message(message.channel, "probing...")
            host = findHost(message)
            stat = 'node_disk_bytes_written{device="sda"}'
            for each in getRate(stat, host):
                await client.send_message(message.channel, each)
                time.sleep(1)
    if "temperature" in message.content.lower():
        t1, t2, t3, t4, t5, t6 = 0,0,0,0,0,0
        for line in requests.get("http://10.0.15.222:8010").text.split('\n'):
            if line.startswith("temperature_celsius{id=\"28-8000001f275f\"}"):
                t1 = line.split()[1]
            elif line.startswith("temperature_celsius{id=\"28-800000271f0b\"}"):
                t2 = line.split()[1]
            elif line.startswith("temperature_celsius{id=\"28-80000026d9c9\"}"):
                t3 = line.split()[1]
            elif line.startswith("temperature_celsius{id=\"28-80000026b96f\"}"):
                t4 = line.split()[1]
            elif line.startswith("temperature_celsius{id=\"28-800000266985\"}"):
                t5 = line.split()[1]
            elif line.startswith("temperature_celsius{id=\"28-800000265472\"}"):
                t6 = line.split()[1]
        msg = '''\
Behind Rack 1: {0}
Behind Rack 2: {1}
Behind Rack 3: {2}
Door AC: {3}
Middle AC: {4}
Wall AC: {5}
'''.format(t1, t2, t3, t6, t5, t4)
        await client.send_message(message.channel, msg)

def getRate(stat, host):
    lastRead = None
    counter = 0
    res = []
    while counter < 10:
        if lastRead is None:
            lastRead = float(getStat(stat, host))
            next
        else:
            currRead = float(getStat(stat, host))
            readRate = currRead - lastRead
            msg = "[" + str(counter+1) + "/10]    " + str(sizeFormat(readRate)) + "/s"
            lastRead = currRead
            time.sleep(1)
            counter += 1
            res.append(msg)
            next
    return res

def sizeFormat(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)



def getStat(stat, host):
    for line in requests.get("http://{0}:9100/metrics".format(host)).text.split('\n'):
        if line.startswith(stat):
            return line.split()[1]


def findHost(message):
    for each in message.content.lower().split():
        if isAlive(each):
            return each


def usage(stat, message):
        if stat in message.content.lower() and "use" in message.content.lower():
            host = findHost(message)
            msg = "Getting {0} in use on {1}".format(stat, host)
            client.send_message(message.channel, msg)
            time.sleep(1)
            url = "http://{0}:9100/metrics".format(host)
            data = requests.get(url).text
            total = 0
            free = 0
            for line in data.split('\n'):
                if "memory" in stat:
                    activemem = 0
                    if line.startswith('node_memory_Active'):
                        activemem = float(line.split()[1])
                        return activemem
                elif "storage" in stat:
                    if line.startswith('node_filesystem_size{device="rootfs",fstype="rootfs",mountpoint="/"}'):
                        total = float(line.split()[1])
                    elif line.startswith('node_filesystem_free{device="rootfs",fstype="rootfs",mountpoint="/"}'):
                        free = float(line.split()[1])
                    if total != 0 and free != 0:
                        used = (total-free)
                        return used
                else:
                    return None




@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----')

def isAlive(host):
    return not bool(os.system("ping -c 1 {0} 2>&1 >/dev/null".format(host)))



client.run(TOKEN)

