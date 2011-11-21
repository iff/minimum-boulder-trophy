#!/usr/bin/python

import datetime
import time
import os
import sys

import math
import pylab
import numpy
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from operator import itemgetter

"""
A very simple script to rank contestants at the Minimum Plauschwettkampf
"""

grades_color = { '0' : '0xfff000', '1' : '0x00ff30', '2' : '0xff4e00', '3' : '0x0006ff', '4' : '0xff0000', '5' : '0xffffff' }
grades_abbrev = [ 'Ge:', 'Gr:', 'Or:', 'Bl:', 'Ro:', 'We:' ]
grade_mapping = [-1,2,0,1,2,3,1,5,2,3,1,2,1,1,0,3,1,2,4,2,3,0,4,2,1,2,3,2,4,2,0,1,1,3,4,5,3,2,3,1,3,0,1,2,2,3,4,5,4,2,1]

# parameters
numFinalists = 4
totalPointsPerBoulder = 100.0


"""
read results
"""
def getResults():
    f = open("data/results")
    results_m = []
    results_w = []
    while f:
        line = f.readline()
        if not line: break

        entry = line.rstrip('\n').split(":")
        if entry[1] == 'w':
            results_w.append(entry)
        elif entry[1] == 'm':
            results_m.append(entry)
        else:
            print("ERROR: unspecified gender!!")
    f.close()
    return (results_m, results_w)


def compileRanking(results):
    bpoints = [0] * len(grade_mapping)

    for res in results:
        if not res[2] == "":
            boulders = res[2].split(",")
            for boulder in boulders:
                bpoints[int(boulder)] = bpoints[int(boulder)] + 1

    for i in range(0, len(bpoints)):
        if bpoints[i] > 0:
            bpoints[i] = totalPointsPerBoulder/bpoints[i]

    ranking = []
    for res in results:
        boulders = res[2].split(",")
        points = 0.0
        if not res[2] == "":
            for boulder in boulders:
                points = points + bpoints[int(boulder)]
        ranking.append([res[0], res[1], points])

    ranking = sorted(ranking, key=lambda x: x[2], reverse=True)

    return ranking


"""
plot ranking in horizontal bars (starting with first)
input assumed be ordered first-to-last (will be reversed for plotting)
"""
def plotRanking(bars, names, title, filename):
    bars.reverse()
    names.reverse()

    #color finalists red, rest gray
    colors = ['#707070'] * (len(bars)-numFinalists)
    finalists = ['#e30000'] * numFinalists
    colors += finalists

    fig_width_pt = 1000.0
    inches_per_pt = 1.0/72.27               # Convert pt to inch
    golden_mean = (math.sqrt(5)-1.0)/2.0    # Aesthetic ratio
    fig_width = fig_width_pt*inches_per_pt  # width in inches
    fig_height = fig_width*golden_mean      # height in inches
    fig_size =  [fig_width,fig_height]
    params = {'backend': 'ps',
              'axes.labelsize': 10,
              'text.fontsize': 10,
              'legend.fontsize': 10,
              'xtick.labelsize': 8,
              'ytick.labelsize': 8,
              'text.usetex': False,
              'figure.figsize': fig_size}
    pylab.rcParams.update(params)

    xlocations = numpy.array(range(len(bars))) + 0.5
    height = 0.5
    fig = pylab.figure()
    ax = fig.add_subplot(1,1,1)
    ax.barh(xlocations, bars, height=height, color=colors)
    ax.xaxis.grid(color='gray', linestyle='dashed')
    plt.yticks(xlocations + height/2, names)
    plt.ylim(0, xlocations[-1] + height*2)
    plt.title(title)
    fig.autofmt_xdate()
    pylab.savefig(filename)


"""
plot mean ascends per grade
input assumed to be ordered yellow-to-white
"""
def plotGrades(data):
    bgrade = [0] * len(grades_abbrev)

    for res in data:
        if not res[2] == "":
            boulders = res[2].split(",")
            for boulder in boulders:
                bgrade[grade_mapping[int(boulder)]] = bgrade[grade_mapping[int(boulder)]] + 1

    mean_ascends_grade = map(lambda x: round(float(x)*100.0/(len(data)*grade_mapping.count(bgrade.index(x))),2), bgrade)

    print(mean_ascends_grade)
    print("")

    xlocations = numpy.array(range(len(mean_ascends_grade))) + 0.5
    width = 0.5
    plt.clf()
    fig = pylab.figure()
    ax = fig.add_subplot(1,1,1)
    ax.bar(xlocations, mean_ascends_grade, width=width, color=['#fff000','#00ff30','#ff4e00','#0006ff','#ff0000','#ffffff'])
    ax.yaxis.grid(color='gray', linestyle='dashed')
    plt.xticks(xlocations + width/2, ["gelb", "gruen", "orange", "blau", "rot", "weiss"])
    plt.xlim(0, xlocations[-1]+width*2)
    plt.title("ascends per grade [%]")
    fig.autofmt_xdate()
    pylab.savefig("mean_ascend")


def printRanking(ranking):
    for i in range(0, len(ranking)):
        print(str(i+1) + ": " + ranking[i][0] + " (" + str(round(ranking[i][2],0)) + ")")
        if i==(numFinalists-1): print("------------------------------")

    print("")


"""
main method
"""
def main(argv):
    results = getResults()
    (maleRanking, femaleRanking) = map(lambda x: compileRanking(x), results)

    printRanking(maleRanking)
    printRanking(femaleRanking)

    max = maleRanking[0][2]
    barsm = map(lambda x: round(x[2]*100/max,0), maleRanking)
    names = map(lambda x: str(maleRanking.index(x)+1) + ": " + x[0], maleRanking)
    plotRanking(barsm, names, "Ranking M", "male")
    barsm.reverse()

    max = femaleRanking[0][2]
    barsf = map(lambda x: round(x[2]*100/max,0), femaleRanking)
    names = map(lambda x: str(femaleRanking.index(x)+1) + ": " + x[0], femaleRanking)
    plotRanking(barsf, names, "Ranking F", "female")
    barsf.reverse()

    plotGrades(results[0]+results[1])

    htmlfile = "results.html"
    file = open(htmlfile, "w")
    file.writelines("<html><head><meta http-equiv=\"refresh\" content=\"60\" ><title>Results Minimum Bouldertrophy</title></head><body>\n")
    file.writelines("<h1>Results Minimum Bouldertrophy</h1>\n")
    file.writelines("<div align=\"center\"><img src=\"male.png\"/></div>\n")
    file.writelines("<div align=\"center\"><img src=\"female.png\"/></div>\n")
    file.writelines("<div align=\"center\"><img src=\"mean_ascend.png\"/></div>\n")
    file.writelines("<hr style=\"background: #393939; border:0; height:3px; margin 30px 0;\"/>\n")
    file.writelines("</br>")
    file.writelines("<div align=\"center\">\n")
    file.writelines("<table border=\"0\" style=\"border-collapse: collapse;\">\n")
    file.writelines("<tr>\n")
    file.writelines("<td valign=\"top\" width=\"400\">\n")

    file.writelines("<table border=\"1\" style=\"border-collapse: collapse;\">\n")
    file.writelines("<tr>\n")
    file.writelines("<th style=\"background: #CCC;\">Rank</th>")
    file.writelines("<th style=\"background: #CCC;\">Name</th>")
    file.writelines("<th style=\"background: #CCC;\">Points</th>\n")
    file.writelines("</tr>\n")
    for i in range(0, len(maleRanking)):
        file.writelines("<tr>\n")
        if i < numFinalists:
            file.writelines("<td style=\"background: #e80000;\">" + str(i+1) + "</td>")
            file.writelines("<td style=\"background: #e80000;\">" + maleRanking[i][0] + "</td>")
            file.writelines("<td style=\"background: #e80000;\">" + str(barsm[i]) + "</td>\n")
        else:
            file.writelines("<td>" + str(i+1) + "</td>")
            file.writelines("<td>" + maleRanking[i][0] + "</td>")
            file.writelines("<td>" + str(barsm[i]) + "</td>\n")
        file.writelines("</tr>\n")
    file.writelines("</table>")
    file.writelines("</td>\n")

    file.writelines("<td valign=\"top\" width=\"400\">\n")
    file.writelines("<table border=\"1\" style=\"border-collapse: collapse;\">\n")
    file.writelines("<tr>\n")
    file.writelines("<th style=\"background: #CCC;\">Rang</th>")
    file.writelines("<th style=\"background: #CCC;\">Name</th>")
    file.writelines("<th style=\"background: #CCC;\">Punkte</th>\n")
    file.writelines("</tr>\n")
    for i in range(0, len(femaleRanking)):
        file.writelines("<tr>\n")
        if i < numFinalists:
            file.writelines("<td style=\"background: #e80000;\">" + str(i+1) + "</td>")
            file.writelines("<td style=\"background: #e80000;\">" + femaleRanking[i][0] + "</td>")
            file.writelines("<td style=\"background: #e80000;\">" + str(barsf[i]) + "</td>\n")
        else:
            file.writelines("<td>" + str(i+1) + "</td>")
            file.writelines("<td>" + femaleRanking[i][0] + "</td>")
            file.writelines("<td>" + str(barsf[i]) + "</td>\n")
        file.writelines("</tr>\n")
    file.writelines("</table>")
    file.writelines("</td>\n")
    file.writelines("</tr>\n")
    file.writelines("</table>")
    file.writelines("</div>\n")
    file.writelines("</body></html>")


if __name__ == "__main__":
    main(sys.argv[1:])
