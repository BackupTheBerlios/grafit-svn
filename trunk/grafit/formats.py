import sys
import os
import zlib
import bz2
import StringIO
import pickle

import ElementTree as xml

from grafit import Worksheet, Graph

def load(project, filename): 
    f = open(filename)
    header = f.read(10)

    data = f.read()
    if header == 'GRAPHITEGZ':
        data = zlib.decompress(data)
    elif header == 'GRAPHITEBZ':
        data = bz2.decompress(data)

    sio = StringIO.StringIO(data)
    try:
        tree = xml.parse(sio)
    finally:
        f.close()
        sio.close()

    root = tree.getroot()

    for welem in root.findall('Worksheet'):
        wsheet = project.new(Worksheet, welem.get("name"))

        for celem in welem:
            if celem.tag == 'CalcColumn':
                setattr(wsheet, celem.get("name"), [])
            elif celem.tag == 'Column':
                safedict = {"__builtins__": { 'True':True, 'False':False, 'None':None}}
                setattr(wsheet, celem.get("name"), pickle.loads(eval(celem.text, safedict)))

    for gelem in root.findall('Graph'):
        graph = project.new(Graph, eval(gelem.get("name")))

    def from_element (self, elem):
        """starting with an empty graph, reconstruct the graph represented by an XML element"""
        # root
        self.freeze()
        self.name = pyget (elem, "name")
        # axes
        prog = project.mainwin.progressbar.progress()
        for aelem in elem.findall ('Axis'):
            axisid = pyget (aelem, "id")
            if axisid == QwtPlot.xBottom:
                axis = self.xaxis
            elif axisid == QwtPlot.yLeft:
                axis = self.yaxis
            else:
                continue
            axis.min, axis.max = pyget (aelem, "limits")
            axis.logscale = pyget (aelem, "logscale")
            axis.title = pyget (aelem, "title")
        # datasets
        for delem in elem.findall ('Dataset'):
            # data
            wsheet = project.w[pyget (delem, "worksheet")]
            colx = pyget (delem, "xcolumn")
            coly = pyget (delem, "ycolumn")
            rangemin, rangemax = pyget (delem, "range")
            ds = self.add(wsheet, colx, coly, rangemin, rangemax)
            # line and symbol styles
            for prop in Dataset.props:
                    ds.set_curve_style(prop, pyget(delem, prop))
        for delem in elem.findall ('FitWindow'):
            self.fitwin.from_element(delem)
        project.mainwin.progressbar.setProgress(prog+len(elem))
        try:
            self.notes.setText(pyget(elem, "notes"))
        except:
            pass
        self.unfreeze()


    def from_element(self, elem):
        self.destroy_ui()
        self.functions = []
        try:
            instnames = pyget(elem, "inst_names")
        except:
            instnames = [None for f in pyget(elem, "names")]

        try:
            self.extra_properties = pyget(elem, "extra_properties")
        except:
            pass

        try:
            self.maxiter = pyget(elem, "max_iterations")
        except:
            pass

        try:
            self.resultsws = pyget(elem, "resultsws")
        except:
            pass

        for name, varshare, instname in zip(pyget(elem, "names"), pyget(elem, "varshares"), instnames):
            try:
                id = [f.name for f in self.available_functions].index(name)
            except ValueError: # function not available
                print >>sys.stderr, "Function not available: %s" % (name,)
                continue
            func = function_class_from_function(self.available_functions[id])()
            func.varshare = varshare
            func.inst_name = instname
            self.functions.append(func)
        self.graph.fitdatasets = [self.graph.datasets[i] for i in pyget(elem, "datasets")]
        self.params_flat_to_func(pyget(elem, "params")[0])
        self.build_ui()


if __name__ == '__main__':
    load(sys.argv[1])
