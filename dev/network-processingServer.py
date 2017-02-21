#!/usr/bin/python3

import dh.image
import dh.network


###
#%% main
###


class Server(dh.network.ImageProcessingServer):
    @staticmethod
    def process(data, params):
        return data
        #return dh.image.gamma(data, params["gamma"])


def main():
    S = Server()
    S.run()


if __name__ == "__main__":
    main()

