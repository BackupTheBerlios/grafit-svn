def fitfunction (*args):
    if len(args) == 3:
        niter, actred, wss = args
        message  = 'Fitting: Iteration %d, xsqr=%g, reduced by %g' % (niter, wss, actred)
        print >>sys.stderr, message
        return
    else:
        params, x = args

    fitdatasets = FitWindow.inst.graph.fit_datasets()
    fsdizes = [len(d.x()) for d in fitdatasets]
    xreal = map (Numeric.array, splitlist (x, fsdizes))

    y = []
    FitWindow.inst.params_flat_to_func (params)
    for i, xx in enumerate(xreal):
        for fn in FitWindow.inst.functions:
            fn.load (fitdatasets[i].curveid)
        y.append (FitWindow.inst.call(xx))
    ret = concatenate (y)
    if FitWindow.inst.graph.fitwin.wmethod == 2:
        try:
            return Numeric.log(ret) # logarithmic fit
        except:
            print >>sys.stderr, 'Math range error (den Vogel)'
            return zeros(ret.shape, 'f')
    else:
        return ret # linear fit
