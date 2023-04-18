#!/usr/bin/env python3

import dh.image
import dh.network


###
#%% main
###


class Server(dh.network.ImageProcessingServer2):
    @staticmethod
    def process(data, params):
        info = {"message": "OK"}
        if ("gamma" in params) and (params["gamma"] is not None):
            result = dh.image.gamma(data, params["gamma"])
        else:
            result = data
        return (result, info)


def main():
    S = Server()
    S.run()


if __name__ == "__main__":
    main()

