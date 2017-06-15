#!/usr/bin/python3

import dh.image
import dh.network


###
#%% main
###


class Server(dh.network.ImageProcessingServer):
    @staticmethod
    def process(data, params):
        if ("gamma" in params) and (params["gamma"] is not None):
            return dh.image.gamma(data, params["gamma"])
        else:
            return data


def main():
    S = Server()
    S.run()


if __name__ == "__main__":
    main()

