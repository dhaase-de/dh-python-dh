#!/usr/bin/python3

import random

import dh.plot


def makeCluster(pointCount=10, mu=(0.0, 0.0), sigma=1.0):
    xs = tuple(random.gauss(mu=mu[0], sigma=sigma) for nPoint in range(pointCount))
    ys = tuple(random.gauss(mu=mu[1], sigma=sigma) for nPoint in range(pointCount))
    return (xs, ys)


def main():
    clusterCount = 7
    pointsPerCluster = 50
    xs = []
    ys = []
    labels = []
    for nCluster in range(clusterCount):
        cluster = makeCluster(pointsPerCluster, ((random.random() - 0.5) * 15.0, (random.random() - 0.5) * 15.0))
        xs += cluster[0]
        ys += cluster[1]
        labels += [chr(97 + nCluster)] * pointsPerCluster

    dh.plot.scatter(xs, ys, labels=labels, colormap="plot")


if __name__ == "__main__":
    main()