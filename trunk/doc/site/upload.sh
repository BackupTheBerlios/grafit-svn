#!/bin/sh
rsync --delete --exclude upload.sh -Cavze  ssh .  danielf@grafit.sarovar.org:/var/lib/gforge/chroot/home/groups/grafit/htdocs/
