import os
import vtk
import json
import numpy
import pandas
from vtk.util import numpy_support
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.tri import Triangulation
from scipy.spatial import KDTree
from PyQt5.QtCore import QFile, QIODevice, QTextStream

import resources


def sort_perimeter(data):
    """Sort a pool of points in perimeter order"""

    pool    = numpy.array(data)
    query   = pool[0, :]
    pool    = pool[1:, :]
    order   = [0]
    idx     = numpy.arange(pool.shape[0]) + 1 

    for j in range(len(data)):
        if pool.shape[0] == 1:
            order.append(idx[0])
            break

        tree    = KDTree(pool)
        d, i    = tree.query(query)
        order.append(idx[i])
        query   = pool[i, :]
        pool    = numpy.delete(pool, i, axis=0)
        idx     = numpy.delete(idx, i, axis=0)

    order   = numpy.take(data, order, axis=0)
    order   = numpy.vstack((order, order[0, :]))
    return order


def read_stl(filename, triangulation=False):
    """Read an ASCII or binary STL file"""
    
    if not os.path.exists(filename):
        return None if not triangulation else None, None

    # Read in the STL with VTK
    reader  = vtk.vtkSTLReader()
    reader.SetFileName(filename)
    reader.Update()
    data    = reader.GetOutput()
    points  = numpy_support.vtk_to_numpy(data.GetPoints().GetData())

    if not triangulation:
        return points

    # Compute the average normal
    normals_filter  = vtk.vtkPolyDataNormals()
    normals_filter.SetInputData(data)
    normals_filter.ComputeCellNormalsOn()
    normals_filter.Update()
    
    normals_data    = normals_filter.GetOutput().GetPointData().GetNormals()
    normals         = numpy_support.vtk_to_numpy(normals_data)
    normals_mean    = numpy.mean(normals_data, axis=0)
    normals_ordered = numpy.argsort(numpy.absolute(normals_mean))
    axes            = sorted(normals_ordered[:-1])
    normal_idx      = normals_ordered[-1]
   
    # Extract the border
    feature_edges   = vtk.vtkFeatureEdges()
    feature_edges.SetInputData(data)
    feature_edges.BoundaryEdgesOn()
    feature_edges.FeatureEdgesOff()
    feature_edges.NonManifoldEdgesOff()
    feature_edges.ManifoldEdgesOff()
    feature_edges.Update()
    border  = numpy_support.vtk_to_numpy(feature_edges.GetOutput().GetPoints().GetData())
    border  = sort_perimeter(border)

    # Compute the triangulation
    n           = data.GetNumberOfCells()
    triangles   = numpy.ndarray((n, 3), dtype=numpy.int64)
    for i in range(n):
        triangles[i, :] = [data.GetCell(i).GetPointId(j) for j in range(3)]

    x               = points[:, axes[0]]
    y               = points[:, axes[1]]
    triangulation   = Triangulation(x, y, triangles=triangles)
    return points, triangulation, axes, border



def read_d1(filename):
    """Read a D1.asc file (raw Windshear data)"""
    
    skiprows            = [0, 1, 2, 4]
    data                = pandas.read_csv(filename, skiprows=skiprows, delimiter="\t")
    data["YAW"]         = data.YAW.round(2)
    data["RRS_SPEED"]   = data.RRS_SPEED.round(1)
    data["run_point"]   = data["Run Number"].round(0).astype(str) + "." + data["Point Number"].round(0).astype(str).str.zfill(2)
    data["run_point"]   = data.run_point.astype(str)
    return data


def read_channel_map(filename):
    """Read a channel map CSV file (x, y, z, channel)"""
    return pandas.read_csv(filename, delimiter=",")


def read_colormap(filename, resource=True):
    """Read a ParaView JSON colormap file"""

    if not os.path.exists(filename) and not resource:
        return None

    if resource:
        stream  = QFile(":static/colormaps/{}".format(filename))
        stream.open(QIODevice.ReadOnly)
        text    = QTextStream(stream).readAll()
        data    = json.loads(text)[0]
        stream.close()

    else:
        with open(filename, "r") as f:
            data    = json.load(f)[0]
        
    name    = data.get("Name", "New Colormap")
    colors  = data.get("RGBPoints", [])
    n       = int(len(colors)/4)
    colors  = numpy.array(colors).reshape((n, 4))

    return LinearSegmentedColormap.from_list(name, colors[:, 1:])



