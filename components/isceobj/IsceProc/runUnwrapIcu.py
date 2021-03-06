#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Copyright 2014 California Institute of Technology. ALL RIGHTS RESERVED.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# United States Government Sponsorship acknowledged. This software is subject to
# U.S. export control laws and regulations and has been classified as 'EAR99 NLR'
# (No [Export] License Required except when exporting to an embargoed country,
# end user, or in support of a prohibited end use). By downloading this software,
# the user agrees to comply with all applicable U.S. export laws and regulations.
# The user has the responsibility to obtain export licenses, or other export
# authority as may be required before exporting this software to any 'EAR99'
# embargoed foreign country or citizen of those countries.
#
# Authors: Kosal Khun, Marco Lavalle
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



# Comment: Adapted from InsarProc/UnwrapIcu.py
import logging
import isceobj
from mroipac.icu.Icu import Icu
import os
# giangi: taken Piyush code grass.py and adapted
logger = logging.getLogger('isce.isceProc.runUnwrap')

def runUnwrap(self):
    infos = {}
    for attribute in ['topophaseFlatFilename', 'unwrappedIntFilename']:
        infos[attribute] = getattr(self._isce, attribute)

    for sceneid1, sceneid2 in self._isce.selectedPairs:
        pair = (sceneid1, sceneid2)
        for pol in self._isce.selectedPols:
            resampAmpImage = self._isce.resampAmpImages[pair][pol]
            sid = self._isce.formatname(pair, pol)
            infos['outputPath'] = os.path.join(self.getoutputdir(sceneid1, sceneid2), sid)
            run(resampAmpImage, infos, sceneid=sid)


def run(resampAmpImage, infos, sceneid='NO_ID'):
    logger.info("Unwrapping interferogram using ICU: %s" % sceneid)
    wrapName = infos['outputPath'] + '.' + infos['topophaseFlatFilename']
    unwrapName = infos['outputPath'] + '.' + infos['unwrappedIntFilename']

    #Setup images
    ampImage = resampAmpImage.copy(access_mode='read')
    width = ampImage.getWidth()

    #intImage
    intImage = isceobj.createIntImage()
    intImage.initImage(wrapName, 'read', width)
    intImage.createImage()

    #unwImage
    unwImage = isceobj.Image.createUnwImage()
    unwImage.setFilename(unwrapName)
    unwImage.setWidth(width)
    unwImage.imageType = 'unw'
    unwImage.bands = 2
    unwImage.scheme = 'BIL'
    unwImage.dataType = 'FLOAT'
    unwImage.setAccessMode('write')
    unwImage.createImage()

    #icuObj = Icu()
    #icuObj.filteringFlag = False      ##insarApp.py already filters it
    icuObj = Icu(name='insarapp_icu')
    icuObj.configure()
    icuObj.initCorrThreshold = 0.1
    icuObj.icu(intImage=intImage, ampImage=ampImage, unwImage = unwImage)

    ampImage.finalizeImage()
    intImage.finalizeImage()
    unwImage.finalizeImage()
    unwImage.renderHdr()

