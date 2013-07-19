#!/bin/bash
rm -rf GoodRunsLists
svn co $ATLASOFF/DataQuality/GoodRunsLists/tags/GoodRunsLists-00-01-05 GoodRunsLists
cd GoodRunsLists/cmt
sed -i 's/#XMLCONFIG=on/XMLCONFIG=on/g' Makefile.Standalone
make -f Makefile.Standalone
