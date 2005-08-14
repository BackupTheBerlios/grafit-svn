all: grafit.msi

grafit.msi: grafit.wixobj
	light grafit.wixobj

grafit.wixobj: grafit.wxs
	candle grafit.wxs
