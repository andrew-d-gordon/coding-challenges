from point_set import *
from line import *
import matplotlib.pyplot as plt
import numpy as np
import sys
import getopt


def plot_points(line: tuple, line_dict: dict, graph: plt):
    """
    :param line: line whose points it crosses should be plotted
    :param line_dict: dict with keys as lines and values as points the lines cross through
    :param graph: graph to plot points on
    :return: None, function serves to plot black points on graph
    """

    points = line_dict[line]
    for p in points:
        graph.plot([p[0]], [p[1]], marker='o', markersize=5, markerfacecolor='black', markeredgecolor='black')


def plot_lines(lines: list, l_d: dict, x_bnd: int = 100, y_bnd: int = 100, g_name: str = '', p_plt: bool = False):
    """
    :param lines: set of lines to be plot (2d, each line specified by tuple (a, b, c) for ax + by = c)
    :param l_d: set of lines with corresponding points which they cross through
    :param x_bnd: desired x bounds for graph, default 100
    :param y_bnd: desired y bounds for graph, default 100
    :param g_name: desired name for plot
    :param p_plt: boolean to decide whether to plot points on graph as well as lines
    :return: None, serves to plot lines on graph and show said graph
    """

    graph = plt
    graph.axis([0-x_bnd, x_bnd, 0-y_bnd, y_bnd])

    # For each line in lines, determine f(x) for each x val within the bounds then plot the line
    for line in lines:
        if line[0] == 0:  # Horizontal lines
            graph.axhline(y=line[2], xmin=0, xmax=1)
        elif line[1] == 0:  # Vertical lines
            graph.axvline(x=line[2], ymin=0, ymax=1)
        else:
            x = np.linspace(0-x_bnd, x_bnd, x_bnd)
            y = [(line[2] - line[0] * v) / line[1] for v in x]  # Solving for f(x) at specified x: y = (c-ax)/b
            graph.plot(x, y)

        # If point plotting is desired, plot corresponding points for line
        if p_plt:
            plot_points(line, l_d, graph)

    # Finish setting graph properties and show graph (add x and y axes, grid lines)
    graph.axhline(y=0, color='k')
    graph.axvline(x=0, color='k')
    graph.grid(True, which='both')
    graph.title(g_name)
    graph.show()


def unique_points(p1: tuple, p2: tuple, points_used: dict, f_n_id: tuple, line_d: dict, point_thresh: int):
    """
    :param p1: the first point of pair in check
    :param p2: the second point of pair in check
    :param points_used: dictionary of use values for points
    :param f_n_id: id of line made by two points
    :param line_d: dictionary containing all lines found so far
    :param point_thresh: number representing how many points a line must cross through in line_d to be part of output
    :return: boolean True or False (True when p_1, p_2 is unique pair and the line between them has reached threshold)
    """

    try:
        if points_used[p1] and points_used[p2] and len(line_d[f_n_id]) >= point_thresh:
            return False
        else:
            return True
    except KeyError:
        return True


def find_unique_lines(p_set: PointSet, num_points: int, point_thresh: int):
    """
    :param p_set: PointSet holding points to process for lines
    :param num_points: number of points to be evaluated (p_set.size)
    :param point_thresh: number of unique points the line must intersect to satisfy
    :return: returns set of lines which intersect satisfiable number (point_thresh) of unique points (UNIQUE SET)
    """

    line_dict = {}
    points_used = p_set.points_d.copy()
    lines_output = []
    str_lines_output = []

    # Build dict of all lines between unique pairs of points in p_set
    # While computing lines, if: line between new pair == previously found line (and threshold met), add line to output
    for i in range(num_points):
        p1 = p_set.points[i]

        # Look at lines between points at idx i (p1) and at idx j=i+1->num_points (p2)
        for j in range(i+1, num_points):
            p2 = p_set.points[j]
            f_n = line_between_points(p1, p2)

            if not unique_points(p1, p2, points_used, f_n.id, line_dict, point_thresh):
                continue

            # If line exists in dict, append new crossed point(s) to the line's crossed point list
            try:
                pts_crossed = line_dict[f_n.id]
                if p1 not in pts_crossed:
                    pts_crossed.append(p1)
                if p2 not in pts_crossed:
                    pts_crossed.append(p2)

                # If line crosses through point_thresh points, add line to output
                if len(pts_crossed) == point_thresh:
                    lines_output.append(f_n.id)
                    str_lines_output.append(f_n.line_str)
            except KeyError:
                # Add line to dict as it is new
                line_dict[f_n.id] = [p1, p2]

            # Set use of points p1 and p2 to True (used)
            points_used[p1] = points_used[p2] = True

    return lines_output, str_lines_output, line_dict


def retrieve_point_list(is_file: bool, input_name: str = '', points: list = []):
    """
    :param input_name: name of input file (if using unit test)
    :param is_file: boolean for if input should be from input_name file or from points param
    :param points: list of points if testing in code input
    :return: returns list of points of form [(x1,y1), ..., (xn,yn)]
    """

    # If input is not a file and valid points list supplied, return said points list
    if not is_file and points is not None:
        return points

    # Validate ability to open and read file
    try:
        f = open(input_name, 'r')
    except OSError:
        print("Error: unable to open/read from input file:", input_name)
        sys.exit(1)

    with f:
        content = f.readlines()
        for p_raw in content:
            p_split = p_raw[:-1].split(' ')  # [:-1) splice removes \n
            if p_split[0] is not None and p_split[1] is not None:
                points.append(tuple([int(p_split[0]), int(p_split[1])]))

    return points


def supply_arguments(d_test: str = 'unit_tests/test_3_set_3', d_pt_thr: int = 3, d_plt_g: bool = False, d_b: int = 20):
    """
    supply_arguments is able to provide a file name, point threshold, and graphing flags for main.
    It does so by attempting to parse the CLI arguments by these flags:
    -t: test file name
    -p: point threshold (1 for graph desired, 0 for graph not desired)
    -g: plot graph of results boolean
    -b: bounds for said graph

    Example CLI run of this program:
    'python find_lines.py -t unit_tests/test_3_set_3 -p 3 -g 1 -b 100'

    :param d_test: default test file to utilize if none supplied
    :param d_pt_thr: default point threshold if none supplied
    :param d_plt_g: default boolean decision for plotting graph when none supplied
    :param d_b: default bounds for graph to plot on
    :return: returns necessary arguments to find test file, process test data, and optional graph flags to be set
    """

    file_name = pt_thresh = plt_graph = graph_bounds = None

    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "t:p:g:b:")
        for opt, arg in opts:
            if opt == '-t':
                file_name = str(arg)
            elif opt == '-p':
                pt_thresh = int(arg)
            elif opt == '-g':
                plt_graph = bool(arg)
            elif opt == '-b':
                graph_bounds = int(arg)
    except getopt.GetoptError:
        print('Error in processing command line arguments.')
        print("Example use: python find_lines.py -t unit_tests/test_3_set_3 -p 3 -g 1 -b 10")
        sys.exit(1)

    if file_name is None:
        file_name = d_test
    if pt_thresh is None:
        pt_thresh = d_pt_thr
    if plt_graph is None:
        plt_graph = d_plt_g
    if graph_bounds is None:
        graph_bounds = d_b

    return file_name, pt_thresh, plt_graph, graph_bounds


if __name__ == '__main__':
    # Retrieve test file name and other vars from CLI/defaults
    test_file, point_threshold, plot_graph, bounds = supply_arguments()
    set_points = []  # Supply own set of points here if desired. [(x1, y1), ..., (xn, yn)]

    # Unit test files be textual to be parsed (.read() specs)
    pts = retrieve_point_list(True, test_file, set_points)

    # Create PointSet object from derived pts list
    ps = PointSet(pts)

    # Find unique lines between three or more points within point set
    pt_lines, pt_str_lines, all_line_dict = find_unique_lines(ps, ps.size, point_threshold)
    print("-------------------\nFinished processing.")
    print("Below are lines which crossed {0} or more points from the test data.".format(point_threshold))
    print("Linear equation form: " + str(pt_str_lines))
    print("Reduced linear equation form: " + str(pt_lines))

    # Graph lines (or points, p_plt=True) in bounded space
    if plot_graph and len(pt_lines) > 0:
        plot_lines(pt_lines, all_line_dict, bounds, bounds, test_file.split('/')[-1], p_plt=True)

    sys.exit(0)