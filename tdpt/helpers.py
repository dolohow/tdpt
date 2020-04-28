def format_speed(speed):
    speed = float(speed)
    if speed < 1000000:
        return '{:.1f} {}'.format(speed/1000, 'kB/s')
    return '{:.1f} {}'.format(speed/1000/1000, 'MB/s')
