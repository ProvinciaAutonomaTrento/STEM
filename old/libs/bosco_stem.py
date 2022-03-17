# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 13:42:07 2015

@author: lucadelu
"""

from __future__ import division
try:
  import readline
except ImportError:
  import pyreadline as readline
from smop.runtime import *

import struct
from sklearn.cluster import KMeans
import numpy as np


def read_las_header(lasFilename=None, *args, **kwargs):
    varargin = cellarray(args)
    nargin = 1-[lasFilename].count(None)+len(args)

    fid = open(lasFilename, "rb")

    lasHeaderInfo = dict()
    lasHeaderInfo['File Signature'] = struct.unpack('4s', fid.read(4))[0]
    lasHeaderInfo['File Source ID'] = struct.unpack('H', fid.read(2))[0]
    lasHeaderInfo['Global Encoding'] = struct.unpack('H', fid.read(2))[0]
    lasHeaderInfo['Project ID - GUID data 1'] = struct.unpack('I',
                                                              fid.read(4))[0]
    lasHeaderInfo['Project ID - GUID data 2'] = struct.unpack('H',
                                                              fid.read(2))[0]
    lasHeaderInfo['Project ID - GUID data 3'] = struct.unpack('H',
                                                              fid.read(2))[0]
    lasHeaderInfo['Project ID - GUID data 4'] = fid.read(8)
    lasHeaderInfo['Version Major'] = struct.unpack('B', fid.read(1))[0]
    lasHeaderInfo['Version Minor'] = struct.unpack('B', fid.read(1))[0]
    lasHeaderInfo['System Identifier'] = struct.unpack('32s', fid.read(32))[0]
    lasHeaderInfo['Generating Software'] = struct.unpack('32s',
                                                         fid.read(32))[0]
    lasHeaderInfo['File Creation Day of Year'] = struct.unpack('H',
                                                               fid.read(2))[0]
    lasHeaderInfo['File Creation Year'] = struct.unpack('H', fid.read(2))[0]
    lasHeaderInfo['Header Size'] = struct.unpack('H', fid.read(2))[0]
    lasHeaderInfo['Offset to point data'] = struct.unpack('I', fid.read(4))[0]
    lasHeaderInfo['Number of variable length records'] = struct.unpack('I', fid.read(4))[0]
    lasHeaderInfo['Point Data Format ID'] = struct.unpack('B', fid.read(1))[0]
    lasHeaderInfo['Point Data Record Length'] = struct.unpack('H',
                                                              fid.read(2))[0]
    lasHeaderInfo['Number of point records'] = struct.unpack('I',
                                                             fid.read(4))[0]
    lasHeaderInfo['Number of points return 1'] = struct.unpack('I',
                                                               fid.read(4))[0]
    lasHeaderInfo['Number of points return 2'] = struct.unpack('I',
                                                               fid.read(4))[0]
    lasHeaderInfo['Number of points return 3'] = struct.unpack('I',
                                                               fid.read(4))[0]
    lasHeaderInfo['Number of points return 4'] = struct.unpack('I',
                                                               fid.read(4))[0]
    lasHeaderInfo['Number of points return 5'] = struct.unpack('I',
                                                               fid.read(4))[0]
    lasHeaderInfo['X scale factor'] = struct.unpack('d', fid.read(8))[0]
    lasHeaderInfo['Y scale factor'] = struct.unpack('d', fid.read(8))[0]
    lasHeaderInfo['Z scale factor'] = struct.unpack('d', fid.read(8))[0]
    lasHeaderInfo['X offset'] = struct.unpack('d', fid.read(8))[0]
    lasHeaderInfo['Y offset'] = struct.unpack('d', fid.read(8))[0]
    lasHeaderInfo['Z offset'] = struct.unpack('d', fid.read(8))[0]
    lasHeaderInfo['Max X'] = struct.unpack('d', fid.read(8))[0]
    lasHeaderInfo['Min X'] = struct.unpack('d', fid.read(8))[0]
    lasHeaderInfo['Max Y'] = struct.unpack('d', fid.read(8))[0]
    lasHeaderInfo['Min Y'] = struct.unpack('d', fid.read(8))[0]
    lasHeaderInfo['Max Z'] = struct.unpack('d', fid.read(8))[0]
    lasHeaderInfo['Min Z'] = struct.unpack('d', fid.read(8))[0]
    disp_([char('Header information from: '), lasFilename])

    # decomment for debug
    #for key, value in lasHeaderInfo.iteritems():
    #    print key, ':', value

    filePos = lasHeaderInfo['Header Size']
    nVarRec = lasHeaderInfo['Number of variable length records']
    if nVarRec > 0:
        if not os.path.exists(char('projection_codes.mat')):
            print 'Cannot display coordinate system because projection_codes.mat file was not found.'
            return lasHeaderInfo
        else:
            load_(char('-mat'), char('projection_codes'))
    for i in arange_(1, nVarRec).reshape(-1):
        fseek_(fid, filePos, char('bof'))
        rsvd = fread_(fid,1,char('uint16=>double'))
        userId = sscanf_(char_(fread_(fid, 16, char('uchar=>uchar')).T),
                         char('%c'))
        recId = fread_(fid, 1, char('uint16=>double'))
        lenRec = fread_(fid, 1, char('uint16=>double'))
        desc = sscanf_(char_(fread_(fid, 32, char('uchar=>uchar')).T),
                       char('%c'))
        filePos = filePos + lenRec + i * 54
        if strcmp_(userId, char('LASF_Projection')) and recId == 34735:
            nTags = floor_(lenRec / 2)
            newFilePos = filePos - lenRec
            fseek_(fid, newFilePos, char('bof'))
            for j in arange_(1, nTags).reshape(-1):
                tag = fread_(fid, 1, char('uint16=>double'))
                index = find_(projectionCodes == tag)
                if not isempty_(index):
                    disp_([char('Coordinate System: '),
                           projectionNames[index]])
                    lasHeaderInfo[37,1:2] = [[[char('Coordinate System')]],
                                             [[projectionNames[index]]]]
    fid.close()
    return lasHeaderInfo


class Object:
    pass


def dec2bin_(l, fill):
    resl = []
    for i, val in enumerate(l):
        res = "{0:#b}".format(val)[2:]
        if fill != 0:
            res = res.zfill(fill)
        resl.append(res)
    return resl


def bin2dec_(l, frm, to):
    resl = []
    for i, val in enumerate(l):
        resl.append(int(val[frm:to], 2))
    return resl


def readInts(fid, formatLength):
    res = []
    while true:
        bytes = fid.read(4)
        if len(bytes) != 4: return res

        res.append(struct.unpack('I', bytes)[0])
        fid.read(formatLength - 4)

    return res


def readShorts(fid, formatLength):
    res = []
    while true:
        bytes = fid.read(2)
        if len(bytes) != 2: return res

        res.append(struct.unpack('H', bytes)[0])
        fid.read(formatLength-2)

    return res


def readBytes(fid, formatLength):
    res = []
    while true:
        bytes = fid.read(1)
        if len(bytes) != 1: return res

        res.append(struct.unpack('B', bytes)[0])
        fid.read(formatLength-1)

    return res


def select_(data, t, index):
    res = []
    for i in range(len(data)):
        if t[i] == index:
            res.append(data[i])

    return res


def readlas_1_2_(filename=None, fwanted=None, vartypewantedstring=None, *args,
                 **kwargs):
    varargin = cellarray(args)
    nargin = 3 - [filename, fwanted, vartypewantedstring].count(None) + len(args)

    vdata = []
    fid = open(filename, "rb")

    header = Object()
    header.fileSignature = struct.unpack('4s', fid.read(4))[0]
    if header.fileSignature != 'LASF':
        print(char('Error: File signature is invalid.'))
    fid.seek(4)
    header.fileSourceID = struct.unpack('H', fid.read(2))[0]
    fid.seek(6)
    header.globalEncoding = struct.unpack('H', fid.read(2))[0]
    fid.seek(8)
    header.projectID_GUIDdata1 = struct.unpack('I', fid.read(4))[0]
    header.projectID_GUIDdata2 = struct.unpack('H', fid.read(2))[0]
    header.projectID_GUIDdata3 = struct.unpack('H', fid.read(2))[0]
    header.projectID_GUIDdata4 = fid.read(8)
    fid.seek(24)
    header.versionMajor = struct.unpack('B', fid.read(1))[0]
    header.versionMinor = struct.unpack('B', fid.read(1))[0]
    header.version = header.versionMajor + header.versionMinor / 10

    if header.version >= 1.1:
        fid.seek(26)
        header.systemID = struct.unpack('32s', fid.read(32))[0]
    else:
        header.systemID = char('0')
    fid.seek(58)
    header.generatingSoftware = struct.unpack('32s', fid.read(32))[0]
    if header.version >= 1.1:
        fid.seek(90)
        header.fileCreationDay = struct.unpack('H', fid.read(2))[0]
    else:
        header.fileCreationDay = 0
    if header.version >= 1.1:
        fid.seek(92)
        header.fileCreationYear = struct.unpack('H', fid.read(2))[0]
    else:
        header.fileCreationYear = 0
    fid.seek(94)
    header.headerSize = struct.unpack('H', fid.read(2))[0]
    fid.seek(96)
    header.pointDataOffset = struct.unpack('I', fid.read(4))[0]
    fid.seek(100)
    header.numberOfVariableRecords = struct.unpack('I', fid.read(4))[0]
    fid.seek(104)
    header.pointDataFormatID = struct.unpack('B', fid.read(1))[0]
    fid.seek(105)
    header.pointDataRecordLength = struct.unpack('H', fid.read(2))[0]
    fid.seek(107)
    header.numberOfPointRecords = struct.unpack('I', fid.read(4))[0]
    fid.seek(111)
    header.numberOfPointsByReturn = []
    header.numberOfPointsByReturn.append(struct.unpack('I', fid.read(4))[0])
    header.numberOfPointsByReturn.append(struct.unpack('I', fid.read(4))[0])
    header.numberOfPointsByReturn.append(struct.unpack('I', fid.read(4))[0])
    header.numberOfPointsByReturn.append(struct.unpack('I', fid.read(4))[0])
    header.numberOfPointsByReturn.append(struct.unpack('I', fid.read(4))[0])
    fid.seek(131)
    header.x = Object()
    header.y = Object()
    header.z = Object()
    header.x.scale = struct.unpack('d', fid.read(8))[0]
    header.y.scale = struct.unpack('d', fid.read(8))[0]
    header.z.scale = struct.unpack('d', fid.read(8))[0]
    header.x.offset = struct.unpack('d', fid.read(8))[0]
    header.y.offset = struct.unpack('d', fid.read(8))[0]
    header.z.offset = struct.unpack('d', fid.read(8))[0]
    header.x.max = struct.unpack('d', fid.read(8))[0]
    header.x.min = struct.unpack('d', fid.read(8))[0]
    header.y.max = struct.unpack('d', fid.read(8))[0]
    header.y.min = struct.unpack('d', fid.read(8))[0]
    header.z.max = struct.unpack('d', fid.read(8))[0]
    header.z.min = struct.unpack('d', fid.read(8))[0]
    if nargin == 2:
        if fwanted[0] == char('A'):
            fwanted = char('xyzirndecskwaupRGBt')
    if nargin < 2:
        if header.pointDataFormatID == 2 or header.pointDataFormatID == 3:
            fwanted = char('xyziRGB')
        else:
            fwanted = char('xyzi')
    hs = header.headerSize
    fid.seek(hs)
    for i in arange_(0, header.numberOfVariableRecords).reshape(-1):
        vdata.append(Object())
        vdata[i].reserved = struct.unpack('H', fid.read(2))[0]
        vdata[i].userID = struct.unpack('16s', fid.read(16))[0]
        vdata[i].recordID = struct.unpack('H', fid.read(2))[0]
        vdata[i].recordLengthAfterHeader = struct.unpack('H', fid.read(2))[0]
        vdata[i].description = struct.unpack('32s', fid.read(32))[0]
        fid.seek(vdata[i].recordLengthAfterHeader)

    disp_('Starting to read point data.')
    c = header.pointDataOffset
    n = header.numberOfPointRecords
    if 0 == header.pointDataFormatID:
        formatLength = 20
    else:
        if 1 == header.pointDataFormatID:
            formatLength = 28
        else:
            if 2 == header.pointDataFormatID:
                formatLength = 26
            else:
                if 3 == header.pointDataFormatID:
                    formatLength = 34
                else:
                    error_('Data format not supported.')
    if header.pointDataFormatID >= 0 and header.pointDataFormatID <= 3:
        fid.seek(c)
        x = readInts(fid, formatLength)
        data = Object()
        data.X = [(el * header.x.scale) + header.x.offset for el in x]

        fid.seek(c + 4)
        y = readInts(fid, formatLength)
        y = [(el * header.y.scale) + header.y.offset for el in y]
        data.Y = y

        if 'z' in fwanted:
            fid.seek(c + 8)
            z = readInts(fid, formatLength)
            z = [(el * header.z.scale) + header.z.offset for el in z]
            data.Z = z

        if 'i' in fwanted:
            fid.seek(c + 12)
            data.intensity = readShorts(fid, formatLength)
        if 'r' in fwanted or 'n' in fwanted or 'd' in fwanted or 'e' in fwanted:
            fid.seek(c + 14)
            returnbyte = readBytes(fid, formatLength)
            returnbyte = dec2bin_(returnbyte, 8)
            if 'r' in fwanted:
                data.returnNumber = bin2dec_(returnbyte, 5, 7)
            if 'n' in fwanted:
                data.numberOfReturns = bin2dec_(returnbyte, 2, 4)
            if 'd' in fwanted:
                data.scanDirection = bin2dec_(returnbyte, 1, 2)
            if 'e' in fwanted:
                data.edgeOfFlightLine = bin2dec_(returnbyte, 0, 1)

        if 'c' in fwanted or 's' in fwanted or 'k' in fwanted or 'w' in fwanted:
            fid.seek(c + 15)
            classbyte = readBytes(fid, formatLength)
            classbyte = dec2bin_(classbyte, 8)
            if 'c' in fwanted:
                data.classification = bin2dec_(classbyte, 3, 7)
            if 's' in fwanted:
                data.synthetic = bin2dec_(classbyte, 2, 3)
            if 'k' in fwanted:
                data.keypoint = bin2dec_(classbyte, 1, 2)
            if 'w' in fwanted:
                data.withheld = bin2dec_(classbyte, 0, 1)

        if 'a' in fwanted:
            fid.seek(c + 16)
            data.scanAngleRank = readBytes(fid, formatLength);
        if 'u' in fwanted:
            fid.seek(c + 17)
            data.userData = readBytes(fid, formatLength);
        if  'p' in fwanted:
            fid.seek(c + 18)
            data.pointSourceID == readShorts(fid, formatLength);
        if 't' in fwanted:
            if header.pointDataFormatID == 1 or header.pointDataFormatID == 3:
                fid.seek(c + 20)
                data.time = readDoubles(fid, formatLength)
            else:
                warning_('GPS time is not supported for this data record format.')
        if 'R' in fwanted or 'G' in fwanted or 'B':
            if header.pointDataFormatID == 2 or header.pointDataFormatID == 3:
                if header.pointDataFormatID == 2:
                    seekpos = 20
                else:
                    seekpos = 28
                if 'R' in fwanted:
                    fid.seek(c + seekpos)
                    data.r = readShorts(fid, formatLength)
                if 'G' in fwanted:
                    fid.seek(c + seekpos + 2)
                    data.g = readShorts(fid, formatLength)
                if 'B' in fwanted:
                    fid.seek(c + seekpos + 4)
                    data.b = readShorts(fid, formatLength)
            else:
                disp_('Color information is not supported for this data record format.')
        disp_('Finished reading point data.')
        data.Geometry = char('Point')
        data.BoundingBox = [[header.x.min, header.y.min],
                            [header.x.max, header.y.max]]
    hs = header.headerSize
    fid.close()
    return data, header, vdata


def perc_cluster_(the_data_tmp=None, the_num_cluster=None, *args, **kwargs):
    if (the_num_cluster <= 0):
        error_(char('the_num_cluster must be greater than zero'))
    perc_min = matlabarray([0, 0.15])
    ok = 0
    while (the_num_cluster != ok and the_num_cluster > 1):

        cluster = zeros_(1, the_num_cluster)
        pnts = []
        for i in range(0, len(the_data_tmp[0])):
            pnts.append([the_data_tmp[0][i], the_data_tmp[1][i],
                         the_data_tmp[2][i]])
        theT = KMeans(n_clusters=the_num_cluster).fit(pnts).labels_

        size_T = len(theT)
        for t in range(size_T):
            cluster[theT[t]] = cluster[theT[t]] + 1
        n = the_num_cluster
        while n > 0:

            percentuale = cluster[n] / size_T
            if percentuale < perc_min[the_num_cluster]:
                the_num_cluster = the_num_cluster - 1
                ok = 0
                n = 1
            else:
                ok = ok + 1
            n = n - 1

    if the_num_cluster == 1:
        pnts = []
        for i in range(0, len(the_data_tmp[0])):
            pnts.append([the_data_tmp[0][i], the_data_tmp[1][i],
                         the_data_tmp[2][i]])
        theT = KMeans(n_clusters=the_num_cluster).fit(pnts).labels_
    return the_num_cluster, theT


def riordina_T_(the_data_temp=None, the_T=None, the_n_layers=None,
                the_media=None, *args, **kwargs):
    if the_n_layers > 1:
        counter = the_n_layers
        T_provv = copy.deepcopy(the_T)
        index = 0
        the_media_provv = copy.deepcopy(the_media)
        while counter > 0:

            max_h_medie = np.max(the_media_provv)
            I = np.argmax(the_media_provv)
            T_provv[the_T == I] = index
            the_media[index] = max_h_medie
            counter = counter - 1
            index = index + 1
            the_media_provv[I] = 0

        the_T = copy.deepcopy(T_provv)
    else:
        the_media = np.mean(the_data_temp[2])
        size_of_T = len(the_T)
        the_T = np.empty(size_of_T)
        the_T.fill(1)
        the_T = the_T.tolist()
    return the_T, the_media


def distanze_layers_(the_data=None, the_n_layers=None, the_T=None,
                     the_media=None, the_delta_h_min=None, *args, **kwargs):
    h_max = []
    h_min = []
    for index in range(the_n_layers):
        sel = select_(the_data[0], the_data[5], index)
        size_data_tmp = len(sel)
        ten_percent = 0.1 * size_data_tmp
        ten_percent = ceil_(ten_percent)
        h_massime = []
        h_minime = []
        data_provv = select_(the_data[2], the_data[5], index)
        for i in range(int(ten_percent)):
            h_massime.append(max_(data_provv))
            for j in range(size_data_tmp):
                if data_provv[j] == h_massime[i]:
                    data_provv[j] = 0
        data_provv = select_(the_data[2], the_data[5], index)
        for i in range(int(ten_percent)):
            h_minime.append(np.min(data_provv))
            for j in range(size_data_tmp):
                if data_provv[j] == h_minime[i]:
                    data_provv[j] = h_massime[0]
        h_max.append(np.mean(h_massime))
        h_min.append(np.mean(h_minime))
    dif_h = (h_min[0] - h_max[1])
    if dif_h < the_delta_h_min:
        the_n_layers, the_T = perc_cluster_(the_data, the_n_layers - 1,
                                            nargout=2)
        the_media = np.mean(the_data[2])
    return the_n_layers, the_T, the_media


def split_layer_(the_data=None, the_T=None, *args, **kwargs):
    varargin = cellarray(args)
    nargin = 2 - [the_data, the_T].count(None) + len(args)

    thickness_min = 9
    R2_min_perc = 0.1
    delta_R = 3
    delta_h = 2
    stacco = 0.3
    changed = 0
    size_data_tmp = len(the_data[0])
    ten_percent = 0.1 * size_data_tmp
    ten_percent = ceil_(ten_percent)
    data_provv = copy.deepcopy(the_data)
    h_massime = []
    h_minime = []
    for i in range(int(ten_percent)):
        h_massime.append(max_(data_provv[2]))
        for j in range(size_data_tmp):
            if data_provv[2][j] == h_massime[i]:
                data_provv[2][j] = 0
    data_provv = copy.deepcopy(the_data)
    for i in range(int(ten_percent)):
        h_minime.append(min_(data_provv[2]))
        for j in range(size_data_tmp):
            if data_provv[2][j] == h_minime[i]:
                data_provv[2][j] = h_massime[0]
    h_max = np.mean(h_massime)
    h_min = np.mean(h_minime)
    if (h_min < 3):
        h_min = 3
    if h_max - h_min > thickness_min:
        counter = 0
        for i in range(size_data_tmp):
            if the_data[3][i] == 2:
                counter = counter + 1
        counter = counter / size_data_tmp
        if counter > R2_min_perc:
            R1 = []
            R2 = []
            for i in range(size_data_tmp):
                if the_data[3][i] == 1:
                    R1.append(the_data[2][i])
                if the_data[3][i] == 2:
                    R2.append(the_data[2][i])
            if len(R1) > 0 and len(R2) > 0:
                R1_mean = np.mean(R1)
                R2_mean = np.mean(R2)
                num_fasce = round_((h_max - h_min) / delta_h)
                fascia = zeros_(1, num_fasce)
                if R1_mean - R2_mean > delta_R:
                    vett_h = the_data[2]
                    size_vett_h = size_(vett_h, 1)
                    current_h = h_min - delta_h / 2
                    for t in range(num_fasce):
                        for i in range(size_vett_h):
                            if vett_h[i] > current_h and vett_h[i] < current_h + delta_h:
                                fascia[t] = fascia[t] + 1
                        current_h = current_h + delta_h
                    min_fascia = min_(fascia)
                    index = np.argmin(fascia)
                    if index != 1 and index != size_(fascia):
                        offset_dx = 1
                        offset_sx = 1
                        while (index + offset_dx) <= num_fasce and fascia[index + offset_dx] == fascia[index]:

                            offset_dx = offset_dx + 1

                        if index + offset_dx > num_fasce:
                            offset_dx = offset_dx - 1
                        while (index - offset_sx) >= 1 and fascia[index - offset_sx] == fascia[index]:

                            offset_sx = offset_sx - 1

                        if index - offset_sx < 1:
                            offset_sx = offset_sx + 1
                        if fascia[index + offset_dx] > fascia[index] and fascia[index - offset_sx] > fascia[index]:
                            if (np.mean(fascia) - fascia[index]) / np.mean(fascia) > stacco:
                                altezza_div_cluster = h_min + index * delta_h - (delta_h / 2)
                                the_new_T = []
                                for index in range(size_data_tmp):
                                    if the_data[index][2] > altezza_div_cluster:
                                        the_new_T.append(1)
                                    else:
                                        the_new_T.append(2)
                                the_n_layers = 2
                                for index in range(the_n_layers):
                                    the_mew_media[index] = np.mean(select_(the_data[2], the_new_T, index))
                                changed = 1
    if changed == 0:
        the_n_layers = 1
        the_new_T = np.copy(the_T)
        the_mew_media = []
    return the_n_layers, the_mew_media, the_new_T


def compute_layers_(the_data_temp=None, *args, **kwargs):
    initial_cluster_num = 2
    delta_h_min = 3
    the_n_layers, the_T = perc_cluster_(the_data_temp, initial_cluster_num,
                                        nargout=2)
    the_media = []
    for i in range(2):
        sel = select_(the_data_temp[2], the_T, i)
        the_media.append(np.mean(sel))
    the_T, the_media = riordina_T_(the_data_temp, the_T, the_n_layers,
                                   the_media, nargout=2)
    if the_n_layers == 2:
        the_data_temp_T = copy.deepcopy(the_data_temp)
        the_data_temp_T.append(the_T)
        the_n_layers, the_T, the_media = distanze_layers_(the_data_temp_T,
                                                          the_n_layers, the_T,
                                                          the_media,
                                                          delta_h_min,
                                                          nargout=3)
    if the_n_layers == 1:
        the_n_layers, the_media, the_T = split_layer_(the_data_temp, the_T,
                                                      nargout=3)
    for i in range(the_n_layers):
        sel = select_(the_data_temp[2], the_T, i)
        the_media.append(np.mean(sel))

    the_T, the_media = riordina_T_(the_data_temp, the_T, the_n_layers,
                                   the_media, nargout=2)
    if the_n_layers == 2:
        the_data_temp_T = copy.deepcopy(the_data_temp)
        the_data_temp_T.append(the_T)
        the_n_layers, the_T, the_media = distanze_layers_(the_data_temp_T,
                                                          the_n_layers, the_T,
                                                          the_media,
                                                          delta_h_min,
                                                          nargout=3)
    the_T, the_media = riordina_T_(the_data_temp, the_T, the_n_layers,
                                   the_media)
    return the_n_layers, the_media, the_T


def compute_types_(the_data_tmp_T=None, the_n_layers=None, the_h_medie=None,
                   *args, **kwargs):
    thickness_min1 = 100
    perc_min = 0.2
    h_sterpaglia = 1
    h_min_type_2 = 7
    diff_mediane = 5
    n_point_bassi = 0
    the_type_prov = 0
    the_type = 0
    size_data_tmp_T = len(the_data_tmp_T[0])
    ten_percent = round_(0.1 * size_data_tmp_T)
    data_provv = copy.deepcopy(the_data_tmp_T)
    h_massime = []
    if ten_percent != 0:
        for i in range(int(ten_percent)):
            h_massime.append(max_(data_provv[2]))
            for j in range(size_data_tmp_T):
                if data_provv[2][j] == h_massime[i]:
                    data_provv[2][j] = 0
    else:
        h_massime.append(max_(the_data_tmp_T[2]))
    max_h = np.mean(h_massime)
    for index in range(size_data_tmp_T):
        if the_data_tmp_T[2][index] < (max_h - h_sterpaglia) / 2:
            n_point_bassi = n_point_bassi + 1
    if the_n_layers == 2 and max_h > h_min_type_2:
        the_type_prov = 2
    else:
        if max_h - the_h_medie < thickness_min1:
            if n_point_bassi != 0:
                perc_n_point = n_point_bassi / size_data_tmp_T
                if perc_n_point < perc_min:
                    h_R1 = select_(the_data_tmp_T[2], the_data_tmp_T[3], 1)
                    h_R2_beta = select_(the_data_tmp_T[2], the_data_tmp_T[3],
                                        2)
                    h_R3_beta = select_(the_data_tmp_T[2], the_data_tmp_T[3],
                                        3)
                    h_R4_beta = select_(the_data_tmp_T[2], the_data_tmp_T[3],
                                        4)
                    h_R2 = copy.deepcopy(h_R2_beta)
                    h_R2.extend(h_R3_beta)
                    h_R2.extend(h_R4_beta)
                    h_R1 = np.sort(h_R1)
                    h_R2 = np.sort(h_R2)
                    size_h_R1 = len(h_R1)
                    size_h_R2 = len(h_R2)
                    if size_h_R2 != 0 and size_h_R1 != 0:
                        mediana_R1 = h_R1[np.ceil(size_h_R1 / 2) - 1]
                        mediana_R2 = h_R2[np.ceil(size_h_R2 / 2) - 1]
                        delta_mediana = np.abs(mediana_R1 - mediana_R2)
                        if delta_mediana < diff_mediane:
                            the_type_prov = 1
                        else:
                            if max_h > h_min_type_2:
                                the_type_prov = 3
                            else:
                                the_type_prov = 1
                    else:
                        the_type_prov = 1
                else:
                    if max_h > h_min_type_2:
                        the_type_prov = 3
                    else:
                        the_type_prov = 1
            else:
                the_type_prov = 1
        else:
            if max_h > h_min_type_2:
                the_type_prov = 3
            else:
                the_type_prov = 1

    the_type = []
    for index in range(size_data_tmp_T):
        the_type.append(the_type_prov)
    return the_type
