"""Analyses the Sheep distances of various Arabia maps."""

# Ok, random thoughts from me.
# Instead of recreating all of the scenarios and running the analysis,
# just output the TC and Sheep coordinates to a csv file.
# Each row is a scenario, the first column is the name of the file,
# the second column is the TC position, and the next 4 columns are the Sheep
# positions.

# And we'll use an autohotkey script to generate lots of scenarios.
# Should probably clean out the scenario directory, maybe that affects
# the time it takes for the menu to load.


from __future__ import annotations
from typing import Dict, List, Tuple
from AoE2ScenarioParser.aoe2_scenario import AoE2Scenario
from AoE2ScenarioParser.datasets.buildings import Building
from AoE2ScenarioParser.datasets.units import Unit
import csv
import math
import os


FAR_THRESHOLD = 23  # Chess distance at which Sheep are considered "far".


# The unit constants for units used as far herdables.
HERDABLES = {
    Unit.COW_A,
    Unit.COW_B,
    Unit.COW_C,
    Unit.COW_D,
    Unit.SHEEP,
}


class Point:
    """An instance represents a 2-dimensional integer point."""

    def __init__(self, x, y):
        """Initializes a new point with coordinates `(float(x), float(y))`."""
        self.x = float(x)
        self.y = float(y)

    def len_chess(self):
        """Returns the chessboard distance of this point to the origin."""
        return Point.dist_chess(self, Point(0.0, 0.0))

    def len_euclid(self):
        """Returns the Euclidean distance of this point to the origin."""
        return Point.dist_euclid(self, Point(0.0, 0.0))

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def str_quote(self) -> str:
        """
        Returns a string representation with double quotation marks.

        Used to surround the comma in points so they play nicely with csv files.
        """
        return f'"{str(self)}"'

    @staticmethod
    def from_str(s: str) -> Point:
        """Constructs a point from a string."""
        s = s.strip()
        comma = s.find(",")
        first = s[1:comma]
        last = s[comma + 1 : len(s) - 1]  # noqa: E203
        return Point(first, last)

    @staticmethod
    def from_str_quote(s: str) -> Point:
        """Constructs a point from a quoted string."""
        s = s.strip()
        comma = s.find(",")
        first = s[2:comma]
        last = s[comma + 2 : len(s) - 2]  # noqa: E203
        return Point(first, last)

    @staticmethod
    def dist_chess(p: Point, q: Point) -> float:
        """Returns the chess distance between `p` and `q`."""
        return max(abs(p.x - q.x), abs(p.y - q.y))

    @staticmethod
    def dist_euclid(p: Point, q: Point) -> float:
        """Returns the Euclidean distance between `p` and `q`."""
        return math.sqrt((p.x - q.x) ** 2 + (p.y - q.y) ** 2)

    @staticmethod
    def center_at(origin: Point, p: Point) -> Point:
        """Returns a `Point` equal to `p` centered around `origin`."""
        return Point(p.x - origin.x, p.y - origin.y)


class MapLocations:
    """An instance represents a map's tc and herdable locations."""

    def __init__(self, name: str, tc: Point, herd: List[Point]):
        """Initializes a map with the give name, tc, and herdable locations."""
        self.name = name
        self.tc = tc
        self.herd = herd

    def __str__(self) -> str:
        herd_strs = [h.str_quote() for h in self.herd]
        strs = [self.name, self.tc.str_quote()] + herd_strs
        return ", ".join(strs)

    @staticmethod
    def from_scn(name: str, scn: AoE2Scenario) -> MapLocations:
        """
        Constructs a `MapLocations` data object from the scenario named `name`
        in scenario object `scn`.
        """
        umgr = scn.unit_manager
        herdables = []
        for u in umgr.get_all_units():
            if u.unit_const in HERDABLES:
                herdables.append(u)
            elif u.unit_const == Building.TOWN_CENTER:
                tc = u
        point_tc = Point(tc.x, tc.y)
        points_herd = [Point(h.x, h.y) for h in herdables]
        return MapLocations(name, point_tc, points_herd)


def write_files_to_csv(dirpath: str, output_fpath: str):
    """
    Parses data from the maps in `dirpath` and writes a csv file of the data.

    Parameters:
        dirpath: A directory containing scenario files to parse.
        output_fpath: The output file to which the csv is written.
    """
    map_locations = []
    for scn_fname in os.listdir(dirpath):
        scn_path = os.path.join(dirpath, scn_fname)
        scn = AoE2Scenario.from_file(scn_path)
        map_locations.append(
            MapLocations.from_scn(scn_fname[: scn_fname.find(".")], scn)
        )
    result = "\n".join(str(d) for d in map_locations)
    with open(output_fpath, "w") as out:
        out.write(result)


def create_csvs():
    """Creates the csv files for analysing the Arabia maps."""
    for name in ("og", "nocow"):
        write_files_to_csv(name, f"{name}.csv")


def convert_to_points(csv_fpath: str) -> List[Point]:
    """
    Returns a list of the coordinates of the herdables in the csv file given
    by `csv_fpath`. The coordinates of the herdables are centered at the town
    center.
    """
    points = []
    with open(csv_fpath) as csvfile:
        locationreader = csv.reader(
            csvfile,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_ALL,
            skipinitialspace=True,
        )
        for row in locationreader:
            tc = Point.from_str(row[1])
            herd = row[2:]
            for h in herd:
                points.append(Point.center_at(tc, Point.from_str(h)))
    return points


def write_offset(name: str):
    """Converts the file with name `name` to a point offset file."""
    csvinput = f"{name}.csv"
    points = convert_to_points(csvinput)
    point_str = "\n".join(str(p) for p in points)
    csvout = f"{name}-offsets.csv"
    with open(csvout, "w") as out:
        out.write(point_str)


def write_offsets():
    """Converts the csv files to point offsets and saves them as csv files."""
    for name in ("og", "nocow", "twogroups"):
        write_offset(name)


def load_offsets(csv_fpath: str) -> List[Point]:
    """Loads the list of points from an offsets csv file."""
    points = []
    with open(csv_fpath) as f:
        for line in f.readlines():
            s = line.strip()
            comma = s.find(",")
            first = s[1:comma]
            last = s[comma + 2 : len(s) - 1]  # noqa: #E203
            p = Point(first, last)
            points.append(p)
    return points


def points_to_lists(pts: List[Point]) -> Tuple[List[float], List[float]]:
    """Converts a list of points to two lists of its coordinates."""
    xs, ys = [], []
    for p in pts:
        xs.append(p.x)
        ys.append(p.y)
    return xs, ys


def convert_offsets_to_cols():
    """Converts the offset files to files for plotting with pgfplots."""
    for name in ("og", "nocow", "twogroups"):
        offset_filename = f"{name}-offsets.csv"
        points = load_offsets(offset_filename)
        strs = ["a, b"]
        for p in points:
            strs.append(f"{p.x}, {p.y}")
        target_filename = f"{name}-columns.csv"
        with open(target_filename, "w") as target:
            target.write("\n".join(strs))


def count_distances(csv_fpath: str):
    """Prints the number of Sheep at each distance."""
    points = load_offsets(csv_fpath)
    chess: Dict[float, int] = {}
    euclid: Dict[float, int] = {}
    for p in points:
        dc = p.len_chess()
        if dc in chess:
            chess[dc] += 1
        else:
            chess[dc] = 1
        de = round(p.len_euclid())
        if de in euclid:
            euclid[de] += 1
        else:
            euclid[de] = 1

    for s, d in (("chess", chess), ("euclid", euclid)):
        print(s)
        for k, v in sorted(d.items()):
            print(f"{k}: {v}")


def print_distances():
    """Prints the distance histograms for the original and DE data."""
    for csvfile in ("og-offsets.csv", "nocow-offsets.csv"):
        count_distances(csvfile)


def minmaxavg():
    """Prints the min, max, and average distances."""
    for name in ("og", "nocow", "twogroups"):
        print(name)
        csvfile = f"{name}-offsets.csv"
        pts = load_offsets(csvfile)
        min_chess = min_euclid = float("infinity")
        max_chess = max_euclid = 0
        avg_chess = avg_euclid = 0.0
        for n, p in enumerate(pts):
            dc = p.len_chess()
            min_chess = min(min_chess, dc)
            max_chess = max(max_chess, dc)
            avg_chess = (n * avg_chess + dc) / (n + 1)
            de = p.len_euclid()
            min_euclid = min(min_euclid, de)
            max_euclid = max(max_euclid, de)
            avg_euclid = (n * avg_euclid + de) / (n + 1)
        print(f"chess - min: {min_chess}, max: {max_chess}, avg: {avg_chess}")
        print(
            f"euclid - min: {min_euclid}, max: {max_euclid}, avg: {avg_euclid}"
        )


def convert_points_to_offsets(csvname: str) -> List[List[Point]]:
    """
    Returns a 2d list where each row is the position of the herdables
    centered around the TC.
    """
    offsets = []
    with open(csvname) as csvfile:
        locationreader = csv.reader(
            csvfile,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_ALL,
            skipinitialspace=True,
        )
        for row in locationreader:
            row_offsets = []
            tc = Point.from_str(row[1])
            herd = row[2:]
            for h in herd:
                herdable_point = Point.from_str(h)
                offset = Point.center_at(tc, herdable_point)
                row_offsets.append(offset)
            offsets.append(row_offsets)
    return offsets


def min4_analysis(name: str):
    """Prints the min4 analysis for either the original or de arabia."""
    print(name)
    offsets = convert_points_to_offsets(f"{name}.csv")
    euclid_distances = [[p.len_euclid() for p in row] for row in offsets]
    min4_counts = {}
    for d in range(12, 43):
        min4_counts[d] = 0
        for row in euclid_distances:
            if all(de >= d for de in row):
                min4_counts[d] += 1
    for d, cnt in sorted(min4_counts.items()):
        print(f"{d}: {cnt}")


def print_min4():
    """Prints the min 4 analysis for the original and DE Arabias."""
    for name in ("og", "nocow", "twogroups"):
        min4_analysis(name)


def main():
    """Runs the script."""
    # Call whatever function you want to run here.
    pass


if __name__ == "__main__":
    main()
