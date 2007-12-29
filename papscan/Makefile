
#PWD = $(shell pwd)
#USER = root
INSTALLDIR = $(PWD)
CONFIG = $(HOME)/papscan.sh
LOG = $(HOME)/papscan.log

.PHONY: config
config:
	sed -i 's;^INSTALLDIR=.*;INSTALLDIR=$(INSTALLDIR);' scan.sh initscan.sh input.sh
	sed -i 's;^CONFIG=.*;CONFIG=$(CONFIG);' input.sh
	sed -i 's;^USER=.*;USER=$(USER);' initscan.sh
	sed -i 's;^LOG=.*;LOG=$(LOG);' input.sh


VERSION = 0.2
DISTNAME = papscan-$(VERSION)
TARNAME = $(DISTNAME).tar.gz
TMP = /tmp
DISTDIR = $(TMP)/$(DISTNAME)
DISTFILES = Makefile README \
            scan.sh input.sh initscan.sh \
            config.sh.sample
BIN_DISTFILES = countinc execheck pnm2pdf pdfgroup renamekeepext scan-script \
                plain monochrome monochrome.py

dist: $(DISTFILES)
	mkdir $(DISTDIR)
	cp $(DISTFILES) $(DISTDIR)
	mkdir $(DISTDIR)/bin
	cd bin; cp $(BIN_DISTFILES) $(DISTDIR)/bin
	cd $(TMP); tar zcf $(TMP)/$(TARNAME) $(DISTNAME)
	mv $(TMP)/$(TARNAME) .
	rm -rf $(DISTDIR)
