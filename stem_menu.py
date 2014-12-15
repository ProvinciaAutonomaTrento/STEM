# -*- coding: utf-8 -*-

"""
***************************************************************************
    stem_menu.py
    ---------------------
    Date                 : August 2014
    Copyright            : (C) 2014 Luca Delucchi
    Email                : luca.delucchi@fmach.it
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Luca Delucchi'
__date__ = 'August 2014'
__copyright__ = '(C) 2014 Luca Delucchi'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "tools"))

from stem_base_dialogs import SettingsDialog


class stem_menu:
    def __init__(self, iface):
        self.iface = iface
        self.stem_menu = None

    def stem_add_submenu(self, submenu):
        if self.stem_menu is not None:
            self.stem_menu.addMenu(submenu)
        else:
            self.iface.addPluginToMenu("&STEM", submenu.menuAction())

    def initGui(self):
        #insert into top-level menu
        self.stem_menu = QMenu(QCoreApplication.translate("STEM", "STEM"))
        self.iface.mainWindow().menuBar().insertMenu(self.iface.firstRightStandardMenu().menuAction(),
                                                     self.stem_menu)
        # Preprocessing Image Submenu
        self.preproc_menu = QMenu(QCoreApplication.translate("STEM",
                                  "&Pre-elaborazione immagini"))
        self.stem_add_submenu(self.preproc_menu)

#        icon = QIcon(os.path.dirname(__file__) + "/icons/stem_animate_columns.png")

        self.preproc_menu.addAction("Filtro riduzione del rumore", self.filter_img)
        self.preproc_menu.addAction("Correzione atmosferica", self.corr_atmo)
        self.preproc_menu.addAction("Segmentazione", self.segmentation)
        self.preproc_menu.addAction("Pansharpening", self.pansharp)
        self.preproc_menu.addAction("Maschera", self.mask_img)
        self.preproc_menu.addAction("Accatastamento", self.multilayer)

        # Pre-Processing LIDAR Submenu
        self.preproc_lidar_menu = QMenu(QCoreApplication.translate("STEM",
                                        "&Pre-elaborazioni LIDAR"))
        self.stem_add_submenu(self.preproc_lidar_menu)

        self.preproc_lidar_menu.addAction("Filtraggio file LAS", self.filterlidar)
        self.preproc_lidar_menu.addAction("Unione file LAS", self.unione)
        self.preproc_lidar_menu.addAction("Ritaglio file LAS", self.clip)
        self.preproc_lidar_menu.addAction("Rasterizzazione file LAS", self.rastlidar)
        self.preproc_lidar_menu.addAction("Estrazione CHM", self.removedtm)

        # Feature Image Submenu
        self.feature_menu = QMenu(QCoreApplication.translate("STEM",
                                  "&Estrazione/selezione feature per"
                                  " la classificazione"))
        self.stem_add_submenu(self.feature_menu)

        self.feature_menu.addAction("Feature di tessitura", self.texture)
        self.feature_menu.addAction("Feature geometriche", self.feat_geom)
        self.feature_menu.addAction("Indici di vegetazione", self.indveg)
        self.feature_menu.addAction("Selezione feature", self.select)

        # Classificazione supervisionata Submenu
        self.class_menu = QMenu(QCoreApplication.translate("STEM",
                                "&Classificazione supervisionata"))
        self.stem_add_submenu(self.class_menu)

        self.class_menu.addAction("Support Vector Machines", self.svm)
        self.class_menu.addAction("Minima distanza", self.class_mindist)
        self.class_menu.addAction("Massima Verosimiglianza", self.class_maxvero)
        self.class_menu.addAction("Spectral Angle Mapper", self.classsap)

        # Post Classificazione Submenu
        self.post_menu = QMenu(QCoreApplication.translate("STEM",
                               "&Post-classificazione"))
        self.stem_add_submenu(self.post_menu)

        self.post_menu.addAction("Attribuzione/modifica classi tematiche", self.clasmod)
        self.post_menu.addAction("Riduzione degli errori", self.error_reduction)
        self.post_menu.addAction("Statistiche", self.stats)
        self.post_menu.addAction("Metriche di accuratezza", self.accu)
        self.post_menu.addAction("K-fold cross validation", self.kfold)

        # Feature LIDAR Submenu
        self.feature_lidar_menu = QMenu(QCoreApplication.translate("STEM",
                                        "&Estrazione feature dalle chiome"))
        self.stem_add_submenu(self.feature_lidar_menu)

        self.feature_lidar_menu.addAction("Delineazione chiome", self.delin)
        self.feature_lidar_menu.addAction("Estrazione feature", self.rastlidar)

        # Stima parametri Submenu
        self.stima_menu = QMenu(QCoreApplication.translate("STEM",
                                "&Stima di parametri"))
        self.stem_add_submenu(self.stima_menu)

        self.stima_menu.addAction("Selezione variabili", self.selvar)
        self.stima_menu.addAction("Stimatore lineare", self.stimlim)
        self.stima_menu.addAction("Support Vector Regression", self.svr)

        # Accuratezza Submenu
        self.valistima_menu = QMenu(QCoreApplication.translate("STEM",
                                    "&Post-elaborazione stima"))
        self.stem_add_submenu(self.valistima_menu)

        self.valistima_menu.addAction("Aggregazione ad aree", self.areeaggr)
        self.valistima_menu.addAction("Metriche di accuratezza", self.accuaccu)
        self.valistima_menu.addAction("K-fold cross validation", self.accukfold)

        self.stem_menu.addAction("&Struttura bosco", self.bosco)
        self.stem_menu.addAction("&Impostazioni", self.settings)

    def unload(self):
        self.iface.mainWindow().menuBar().removeAction(self.stem_menu.menuAction())

    # preprocessing

    def filter_img(self):
        from image_filter import STEMToolsDialog as filter_img_dialog
        dialog = filter_img_dialog(self.iface, "Filtro riduzione del rumore")
        dialog.exec_()

    def corr_geom(self):
        from image_corrgeom import STEMToolsDialog as corr_geom_dialog
        dialog = corr_geom_dialog(self.iface)
        dialog.exec_()

    def corr_atmo(self):
        from image_corratmo import STEMToolsDialog as corr_atmo_dialog
        dialog = corr_atmo_dialog(self.iface, "Correzione atmosferica")
        dialog.exec_()

    def segmentation(self):
        from image_segm import STEMToolsDialog as segmentation_dialog
        dialog = segmentation_dialog(self.iface, "Segmentazione")
        dialog.exec_()

    def pansharp(self):
        from image_pansh import STEMToolsDialog as pansharp_dialog
        dialog = pansharp_dialog(self.iface, "Pansharpening")
        dialog.exec_()

    def registr(self):
        from image_registr import STEMToolsDialog as registr_dialog
        dialog = registr_dialog(self.iface)
        dialog.exec_()

#    def mosaic_img(self):
#        from image_mosaic import STEMToolsDialog as mosaic_img_dialog
#        dialog = mosaic_img_dialog(self.iface)
#        dialog.exec_()

    def mask_img(self):
        from image_mask import STEMToolsDialog as mask_img_dialog
        dialog = mask_img_dialog(self.iface, "Maschera")
        dialog.exec_()

    def multilayer(self):
        from image_multi import STEMToolsDialog as multi_img_dialog
        dialog = multi_img_dialog(self.iface, "Accatastamento")
        dialog.exec_()

#    def reprojection(self):
#        from image_repr import STEMToolsDialog as reprj_img_dialog
#        dialog = reprj_img_dialog(self.iface)
#        dialog.exec_()

    # feature

    def texture(self):
        from feat_texture import STEMToolsDialog as texture_dialog
        dialog = texture_dialog(self.iface, "Feature di tessitura")
        dialog.exec_()

    def feat_geom(self):
        from feat_geometry import STEMToolsDialog as feat_geom_dialog
        dialog = feat_geom_dialog(self.iface, "Feature geometriche")
        dialog.exec_()

    def indveg(self):
        from feat_vege import STEMToolsDialog as indveg_dialog
        dialog = indveg_dialog(self.iface, "Indici di vegetazione")
        dialog.exec_()

    def select(self):
        from feat_select import STEMToolsDialog as select_dialog
        dialog = select_dialog(self.iface, "Selezione feature")
        dialog.exec_()

    # supervised classification

    def svm(self):
        from class_svm import STEMToolsDialog as svm_dialog
        dialog = svm_dialog(self.iface, "Support Vector Machines")
        dialog.exec_()

    def class_mindist(self):
        from class_mindist import STEMToolsDialog as mindist_dialog
        dialog = mindist_dialog(self.iface, "Minima distanza")
        dialog.exec_()

    def class_maxvero(self):
        from class_maxvero import STEMToolsDialog as maxvero_dialog
        dialog = maxvero_dialog(self.iface, "Massima Verosimiglianza")
        dialog.exec_()

    def classsap(self):
        from class_sap import STEMToolsDialog as classap_dialog
        dialog = classap_dialog(self.iface, "Spectral Angle Mapper")
        dialog.exec_()

    # post-elaborazione

    def clasmod(self):
        from clas_mod import STEMToolsDialog as clasmod_dialog
        dialog = clasmod_dialog(self.iface, "Attribuzione/modifica classi tematiche")
        dialog.exec_()

    def error_reduction(self):
        from error_reduction import STEMToolsDialog as error_reduction_dialog
        dialog = error_reduction_dialog(self.iface, "Riduzione degli errori")
        dialog.exec_()

    # validation

    def stats(self):
        from vali_stats import STEMToolsDialog as stats_dialog
        dialog = stats_dialog(self.iface, "Statistiche")
        dialog.exec_()

    def accu(self):
        from vali_accu import STEMToolsDialog as accu_dialog
        dialog = accu_dialog(self.iface, "Metriche di accuratezza")
        dialog.exec_()

    def kfold(self):
        from vali_kfold import STEMToolsDialog as kfold_dialog
        dialog = kfold_dialog(self.iface, "K-fold cross validation")
        dialog.exec_()

    # preproc lidar

    def removedtm(self):
        from las_removedtm import STEMToolsDialog as removedtm_dialog
        dialog = removedtm_dialog(self.iface, "Estrazione CHM")
        dialog.exec_()

    def unione(self):
        from las_union import STEMToolsDialog as union_dialog
        dialog = union_dialog(self.iface, "Unione file LAS")
        dialog.exec_()

    def clip(self):
        from las_clip import STEMToolsDialog as clip_dialog
        dialog = clip_dialog(self.iface, "Ritaglio file LAS")
        dialog.exec_()

    def rastlidar(self):
        from las_extract import STEMToolsDialog as rastlidar_dialog
        dialog = rastlidar_dialog(self.iface, "Rasterizzazione file LAS")
        dialog.exec_()

    def delin(self):
        from feat_delin import STEMToolsDialog as delin_dialog
        dialog = delin_dialog(self.iface, "Delineazione chiome")
        dialog.exec_()

    def filterlidar(self):
        from las_filter import STEMToolsDialog as filterlidar_dialog
        dialog = filterlidar_dialog(self.iface, "Filtraggio file LAS")
        dialog.exec_()

    # stima

    def selvar(self):
        from stim_selvar import STEMToolsDialog as selvar_dialog
        dialog = selvar_dialog(self.iface, "Selezione variabili")
        dialog.exec_()

    def stimlim(self):
        from stim_linear import STEMToolsDialog as stimlim_dialog
        dialog = stimlim_dialog(self.iface, "Stimatore lineare")
        dialog.exec_()

    def svr(self):
        from stim_svr import STEMToolsDialog as svr_dialog
        dialog = svr_dialog(self.iface, "Support Vector Regression")
        dialog.exec_()

    # accuratezza

    def accuaccu(self):
        from post_accu import STEMToolsDialog as accu_dialog
        dialog = accu_dialog(self.iface, "Metriche di accuratezza")
        dialog.exec_()

    def accukfold(self):
        from post_kfold import STEMToolsDialog as kfold_dialog
        dialog = kfold_dialog(self.iface, "K-fold cross validation")
        dialog.exec_()

    def areeaggr(self):
        from post_aggraree import STEMToolsDialog as areeaggr_dialog
        dialog = areeaggr_dialog(self.iface, "Aggregazione ad aree")
        dialog.exec_()

    def bosco(self):
        from bosco import STEMToolsDialog as bosco_dialog
        dialog = bosco_dialog(self.iface, "Struttura bosco")
        dialog.exec_()

    def settings(self):
        dialog = SettingsDialog(self.iface.mainWindow(), self.iface)
        dialog.exec_()
