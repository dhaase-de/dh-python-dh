#!/usr/bin/python3

import argparse

import dh.utils
import dh.image
import dh.hardware.raspi


def main():
    # parse aeguments
    parser = argparse.ArgumentParser(description="Starts a client for remote access to a Raspberry Pi camera.")
    parser.add_argument("host", type=str, help="Host (hostname or IP address) of the server to connect to.")
    parser.add_argument("-p", "--port", type=int, default=7220, help="Port of the server to connect to.")
    args = parser.parse_args()

    # start client
    C = dh.hardware.raspi.CameraClient(host=args.host, port=args.port)
    F = dh.utils.FrequencyEstimator()
    run = True
    while run:
        try:
            params = {}
            I = C.capture(params)

            # show image (with FPS and ping)
            dh.image.text(I, "{} fps".format(dh.utils.around(F.event())), position=(0.0, 0.0), anchor="lt")
            dh.image.text(I, "ping: {} ms".format(dh.utils.around(C.ping() * 1000.0)), position=(1.0, 0.0), anchor="rt")
            dh.image.text(I, "{}:{}".format(args.host, args.port), position=(0.0, 1.0), anchor="lb")
            if dh.image.show(I, wait=10) in dh.utils.qkeys():
                return
        except KeyboardInterrupt:
            # prevent keyboard interrupts within the communication with the server - instead, finish communication and exit gracefully
            print("Exiting gracefully...")
            run = False


if __name__ == "__main__":
    main()
