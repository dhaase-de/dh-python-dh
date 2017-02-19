import dh.plot


if __name__ == "__main__":
    C = dh.plot.GoogleCharts()

    # column chart
    C.append(dh.plot.GoogleColumnChart(
        xs=["a", "b", "c", "d"],
        yss={"bar1": [1, 2, 3, 4], "bar2": [2, 3, 2, 1]},
    ))

    C.append(dh.plot.GoogleColumnChart(
        xs=[1, 2, 3, 4],
        yss=[2, 3, 2, 1],
        options={
            "chartArea": {"width": "50%", "height": "50%"},
        }
    ))

    # scatter chart
    C.append(dh.plot.GoogleScatterChart(
        xs=[3, 5, 3, 5, 4],
        ys=[3, 2, 1, 5, 1],
    ))

    C.append(dh.plot.GoogleScatterChart(
        xs=[3, 5, 3, 5, 4],
        ys=[3, 2, 1, 5, 1],
        labels=["a", "b", "a", "b", "a"],
    ))

    # line chart
    C.append(dh.plot.GoogleLineChart(
        xs=[1, 2, 3, 4, 5],
        yss=[2, 4, 9, 16, 25],
    ))
    C.append(dh.plot.GoogleLineChart(
        xs=[1, 2, 3, 4, 5],
        yss={"**2": [1, 4, 9, 16, 25], "**3": [1, 8, 27, 64, 125]}
    ))

    C.save("/tmp/dh.plot.html")
