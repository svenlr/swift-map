def get_option(file, key):
    with open(file, "r") as f:
        for l in f:
            try:
                (k, v) = l.split('=')
                k = k.strip(' ')
                if k == key:
                    return v.rstrip('\n').rstrip('\r').strip(' ')
            except:
                continue
    return ''


def set_option(file, key, value):
    with open(file, "r") as f:
        new_lines = []
        found = False
        for l in f:
            try:
                (k, v) = l.split('=')
                k = k.strip(' ')
                if k == key:
                    l = str(key) + "=" + str(value) + "\n"
                    found = True
            except Exception as e:
                pass
            new_lines.append(l)
    with open(file, "w") as f:
        for l in new_lines:
            f.write(l)
    return found


def read_file(file_):
    with open(file_) as f:
        return f.read()
