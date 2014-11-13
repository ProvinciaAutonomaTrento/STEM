# --------------------------------------------------------
#    stem_menu - QGIS plugins menu class
#
#    begin                : 19 june 2014
#    copyright            : (c) 2014 Luca Delucchi
#    email                :
#
#   MMQGIS is free software and is offered without guarantee
#   or warranty. You can redistribute it and/or modify it
#   under the terms of version 2 of the GNU General Public
#   License (GPL v2) as published by the Free Software
#   Foundation (www.gnu.org).
# --------------------------------------------------------

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
        self.filter_noise_action = QAction("Filtro riduzione del rumore",
                                           self.iface.mainWindow())
        QObject.connect(self.filter_noise_action, SIGNAL("triggered()"),
                        self.filter_img)
        self.preproc_menu.addAction(self.filter_noise_action)


#        self.corr_geom_action = QAction("Correzione geometrica",
#                                        self.iface.mainWindow())
#        QObject.connect(self.corr_geom_action, SIGNAL("triggered()"),
#                        self.corr_geom)
#        self.preproc_menu.addAction(self.corr_geom_action)

        self.corr_atmo_action = QAction("Correzione atmosferica",
                                        self.iface.mainWindow())
        QObject.connect(self.corr_atmo_action, SIGNAL("triggered()"),
                        self.corr_atmo)
        self.preproc_menu.addAction(self.corr_atmo_action)

        self.segment_action = QAction("Segmentazione", self.iface.mainWindow())
        QObject.connect(self.segment_action, SIGNAL("triggered()"),
                        self.segmentation)
        self.preproc_menu.addAction(self.segment_action)

        self.pansharp_action = QAction("Pansharpening",
                                       self.iface.mainWindow())
        QObject.connect(self.pansharp_action, SIGNAL("triggered()"),
                        self.pansharp)
        self.preproc_menu.addAction(self.pansharp_action)

#        self.registr_action = QAction("Georeferenziazione",
#                                      self.iface.mainWindow())
#        QObject.connect(self.registr_action, SIGNAL("triggered()"),
#                        self.registr)
#        self.preproc_menu.addAction(self.registr_action)

#        self.mosaic_img_action = QAction("Mosaicatura",
#                                         self.iface.mainWindow())
#        QObject.connect(self.mosaic_img_action, SIGNAL("triggered()"),
#                        self.mosaic_img)
#        self.preproc_menu.addAction(self.mosaic_img_action)

        self.mask_img_action = QAction("Maschera", self.iface.mainWindow())
        QObject.connect(self.mask_img_action, SIGNAL("triggered()"),
                        self.mask_img)
        self.preproc_menu.addAction(self.mask_img_action)

        self.multilayer_action = QAction("Accatastamento",
                                         self.iface.mainWindow())
        QObject.connect(self.multilayer_action, SIGNAL("triggered()"),
                        self.multilayer)
        self.preproc_menu.addAction(self.multilayer_action)

#        self.repr_action = QAction("Riproiezione immagini",
#                                   self.iface.mainWindow())
#        QObject.connect(self.repr_action, SIGNAL("triggered()"),
#                        self.reprojection)
#        self.preproc_menu.addAction(self.repr_action)

        # Pre-Processing LIDAR Submenu
        self.preproc_lidar_menu = QMenu(QCoreApplication.translate("STEM",
                                        "&Pre-elaborazioni LIDAR"))
        self.stem_add_submenu(self.preproc_lidar_menu)

        self.filter_action = QAction("Filtraggio file LAS",
                                        self.iface.mainWindow())
        QObject.connect(self.filter_action, SIGNAL("triggered()"),
                        self.filterlidar)
        self.preproc_lidar_menu.addAction(self.filter_action)

        self.unione_action = QAction("Unione file LAS",
                                     self.iface.mainWindow())
        QObject.connect(self.unione_action, SIGNAL("triggered()"), self.unione)
        self.preproc_lidar_menu.addAction(self.unione_action)

        self.clip_action = QAction("Ritaglio file LAS",
                                   self.iface.mainWindow())
        QObject.connect(self.clip_action, SIGNAL("triggered()"), self.clip)
        self.preproc_lidar_menu.addAction(self.clip_action)

        self.rastlidar_action = QAction("Rasterizzazione file LAS",
                                        self.iface.mainWindow())
        QObject.connect(self.rastlidar_action, SIGNAL("triggered()"),
                        self.rastlidar)
        self.preproc_lidar_menu.addAction(self.rastlidar_action)

        self.removedtm_action = QAction("Estrazione CHM",
                                        self.iface.mainWindow())
        QObject.connect(self.removedtm_action, SIGNAL("triggered()"),
                        self.removedtm)
        self.preproc_lidar_menu.addAction(self.removedtm_action)

        # Feature Image Submenu
        self.feature_menu = QMenu(QCoreApplication.translate("STEM",
                                  "&Estrazione/selezione feature per"
                                  " la classificazione"))
        self.stem_add_submenu(self.feature_menu)

        self.texture_action = QAction("Feature di tessitura",
                                      self.iface.mainWindow())
        QObject.connect(self.texture_action, SIGNAL("triggered()"),
                        self.texture)
        self.feature_menu.addAction(self.texture_action)

        self.feat_geom_action = QAction("Feature geometriche",
                                        self.iface.mainWindow())
        QObject.connect(self.feat_geom_action, SIGNAL("triggered()"),
                        self.feat_geom)
        self.feature_menu.addAction(self.feat_geom_action)

        self.indveg_action = QAction("Indici di vegetazione",
                                     self.iface.mainWindow())
        QObject.connect(self.indveg_action, SIGNAL("triggered()"), self.indveg)
        self.feature_menu.addAction(self.indveg_action)

        self.select_action = QAction("Selezione feature",
                                     self.iface.mainWindow())
        QObject.connect(self.select_action, SIGNAL("triggered()"), self.select)
        self.feature_menu.addAction(self.select_action)

        # Classificazione supervisionata Submenu
        self.class_menu = QMenu(QCoreApplication.translate("STEM",
                                "&Classificazione supervisionata"))
        self.stem_add_submenu(self.class_menu)

        self.svm_action = QAction("Support Vector Machines",
                                  self.iface.mainWindow())
        QObject.connect(self.svm_action, SIGNAL("triggered()"), self.svm)
        self.class_menu.addAction(self.svm_action)

        self.class_mindist_action = QAction("Minima distanza",
                                            self.iface.mainWindow())
        QObject.connect(self.class_mindist_action, SIGNAL("triggered()"),
                        self.class_mindist)
        self.class_menu.addAction(self.class_mindist_action)

        self.class_maxvero_action = QAction("Massima Verosimiglianza",
                                            self.iface.mainWindow())
        QObject.connect(self.class_maxvero_action, SIGNAL("triggered()"),
                        self.class_maxvero)
        self.class_menu.addAction(self.class_maxvero_action)

        self.classsap_action = QAction("Spectral Angle Mapper",
                                       self.iface.mainWindow())
        QObject.connect(self.classsap_action, SIGNAL("triggered()"),
                        self.classsap)
        self.class_menu.addAction(self.classsap_action)

        # Post Classificazione Submenu
        self.post_menu = QMenu(QCoreApplication.translate("STEM",
                               "&Post-classificazione"))
        self.stem_add_submenu(self.post_menu)

        self.clasmod_action = QAction("Attribuzione/modifica classi tematiche",
                                      self.iface.mainWindow())
        QObject.connect(self.clasmod_action, SIGNAL("triggered()"),
                        self.clasmod)
        self.post_menu.addAction(self.clasmod_action)

        self.error_reduction_action = QAction("Riduzione degli errori",
                                              self.iface.mainWindow())
        QObject.connect(self.error_reduction_action, SIGNAL("triggered()"),
                        self.error_reduction)
        self.post_menu.addAction(self.error_reduction_action)

        self.stats_action = QAction("Statistiche",
                                    self.iface.mainWindow())
        QObject.connect(self.stats_action, SIGNAL("triggered()"), self.stats)
        self.post_menu.addAction(self.stats_action)

        self.accu_action = QAction("Metriche di accuratezza",
                                   self.iface.mainWindow())
        QObject.connect(self.accu_action, SIGNAL("triggered()"),
                        self.accu)
        self.post_menu.addAction(self.accu_action)

        self.kfold_action = QAction("K-fold cross validation",
                                    self.iface.mainWindow())
        QObject.connect(self.kfold_action, SIGNAL("triggered()"),
                        self.kfold)
        self.post_menu.addAction(self.kfold_action)

        # Feature LIDAR Submenu
        self.feature_lidar_menu = QMenu(QCoreApplication.translate("STEM",
                                        "&Estrazione feature dalle chiome"))
        self.stem_add_submenu(self.feature_lidar_menu)

        self.delin_action = QAction("Delineazione chiome",
                                    self.iface.mainWindow())
        QObject.connect(self.delin_action, SIGNAL("triggered()"), self.delin)
        self.feature_lidar_menu.addAction(self.delin_action)

        self.rastlidar_action = QAction("Estrazione feature",
                                        self.iface.mainWindow())
        QObject.connect(self.rastlidar_action, SIGNAL("triggered()"),
                        self.rastlidar)
        self.feature_lidar_menu.addAction(self.rastlidar_action)

        # Stima parametri Submenu
        self.stima_menu = QMenu(QCoreApplication.translate("STEM",
                                "&Stima di parametri"))
        self.stem_add_submenu(self.stima_menu)

        self.selvar_action = QAction("Selezione variabili",
                                     self.iface.mainWindow())
        QObject.connect(self.selvar_action, SIGNAL("triggered()"),
                        self.selvar)
        self.stima_menu.addAction(self.selvar_action)

        self.stimlin_action = QAction("Stimatore lineare",
                                      self.iface.mainWindow())
        QObject.connect(self.stimlin_action, SIGNAL("triggered()"),
                        self.stimlim)
        self.stima_menu.addAction(self.stimlin_action)

        self.svr_action = QAction("Support Vector Regression",
                                  self.iface.mainWindow())
        QObject.connect(self.svr_action, SIGNAL("triggered()"),
                        self.svr)
        self.stima_menu.addAction(self.svr_action)

        # Accuratezza Submenu
        self.valistima_menu = QMenu(QCoreApplication.translate("STEM",
                                    "&Post-elaborazione stima"))
        self.stem_add_submenu(self.valistima_menu)

        self.areeaggr_action = QAction("Aggregazione ad aree",
                                       self.iface.mainWindow())
        QObject.connect(self.areeaggr_action, SIGNAL("triggered()"),
                        self.areeaggr)
        self.valistima_menu.addAction(self.areeaggr_action)

        self.accuaccu_action = QAction("Metriche di accuratezza",
                                       self.iface.mainWindow())
        QObject.connect(self.accuaccu_action, SIGNAL("triggered()"),
                        self.accuaccu)
        self.valistima_menu.addAction(self.accuaccu_action)

        self.accukfold_action = QAction("K-fold cross validation",
                                        self.iface.mainWindow())
        QObject.connect(self.accukfold_action, SIGNAL("triggered()"),
                        self.accukfold)
        self.valistima_menu.addAction(self.accukfold_action)

        self.bosco_action = QAction(QCoreApplication.translate("STEM",
                                    "&Struttura bosco"),
                                    self.iface.mainWindow())
        QObject.connect(self.bosco_action, SIGNAL("triggered()"),
                        self.bosco)
        self.stem_menu.addAction(self.bosco_action)

        self.settings_action = QAction(QCoreApplication.translate("STEM",
                                       "&Impostazioni"),
                                       self.iface.mainWindow())
        QObject.connect(self.settings_action, SIGNAL("triggered()"),
                        self.settings)
        self.stem_menu.addAction(self.settings_action)

    def unload(self):
        self.iface.mainWindow().menuBar().removeAction(self.stem_menu.menuAction())

    # preprocessing

    def filter_img(self):
        from image_filter import STEMToolsDialog as filter_img_dialog
        dialog = filter_img_dialog(self.iface)
        dialog.exec_()

    def corr_geom(self):
        from image_corrgeom import STEMToolsDialog as corr_geom_dialog
        dialog = corr_geom_dialog(self.iface)
        dialog.exec_()

    def corr_atmo(self):
        from image_corratmo import STEMToolsDialog as corr_atmo_dialog
        dialog = corr_atmo_dialog(self.iface)
        dialog.exec_()

    def segmentation(self):
        from image_segm import STEMToolsDialog as segmentation_dialog
        dialog = segmentation_dialog(self.iface)
        dialog.exec_()

    def pansharp(self):
        from image_pansh import STEMToolsDialog as pansharp_dialog
        dialog = pansharp_dialog(self.iface)
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
        dialog = mask_img_dialog(self.iface)
        dialog.exec_()

    def multilayer(self):
        from image_multi import STEMToolsDialog as multi_img_dialog
        dialog = multi_img_dialog(self.iface)
        dialog.exec_()

#    def reprojection(self):
#        from image_repr import STEMToolsDialog as reprj_img_dialog
#        dialog = reprj_img_dialog(self.iface)
#        dialog.exec_()

    # feature

    def texture(self):
        from feat_texture import STEMToolsDialog as texture_dialog
        dialog = texture_dialog(self.iface)
        dialog.exec_()

    def feat_geom(self):
        from feat_geometry import STEMToolsDialog as feat_geom_dialog
        dialog = feat_geom_dialog(self.iface)
        dialog.exec_()

    def indveg(self):
        from feat_vege import STEMToolsDialog as indveg_dialog
        dialog = indveg_dialog(self.iface)
        dialog.exec_()

    def select(self):
        from feat_select import STEMToolsDialog as select_dialog
        dialog = select_dialog(self.iface)
        dialog.exec_()

    # supervised classification

    def svm(self):
        from class_svm import STEMToolsDialog as svm_dialog
        dialog = svm_dialog(self.iface)
        dialog.exec_()

    def class_mindist(self):
        from class_mindist import STEMToolsDialog as mindist_dialog
        dialog = mindist_dialog(self.iface)
        dialog.exec_()

    def class_maxvero(self):
        from class_maxvero import STEMToolsDialog as maxvero_dialog
        dialog = maxvero_dialog(self.iface)
        dialog.exec_()

    def classsap(self):
        from class_sap import STEMToolsDialog as classap_dialog
        dialog = classap_dialog(self.iface)
        dialog.exec_()

    # post-elaborazione

    def clasmod(self):
        from clas_mod import STEMToolsDialog as clasmod_dialog
        dialog = clasmod_dialog(self.iface)
        dialog.exec_()

    def error_reduction(self):
        from error_reduction import STEMToolsDialog as error_reduction_dialog
        dialog = error_reduction_dialog(self.iface)
        dialog.exec_()

    # validation

    def stats(self):
        from vali_stats import STEMToolsDialog as stats_dialog
        dialog = stats_dialog(self.iface)
        dialog.exec_()

    def accu(self):
        from vali_accu import STEMToolsDialog as accu_dialog
        dialog = accu_dialog(self.iface)
        dialog.exec_()

    def kfold(self):
        from vali_kfold import STEMToolsDialog as kfold_dialog
        dialog = kfold_dialog(self.iface)
        dialog.exec_()

    # preproc lidar

    def removedtm(self):
        from las_removedtm import STEMToolsDialog as removedtm_dialog
        dialog = removedtm_dialog(self.iface)
        dialog.exec_()

    def unione(self):
        from las_union import STEMToolsDialog as union_dialog
        dialog = union_dialog(self.iface)
        dialog.exec_()

    def clip(self):
        from las_clip import STEMToolsDialog as clip_dialog
        dialog = clip_dialog(self.iface)
        dialog.exec_()

    def rastlidar(self):
        from las_extract import STEMToolsDialog as rastlidar_dialog
        dialog = rastlidar_dialog(self.iface)
        dialog.exec_()

    def delin(self):
        from feat_delin import STEMToolsDialog as delin_dialog
        dialog = delin_dialog(self.iface)
        dialog.exec_()

    def filterlidar(self):
        from las_filter import STEMToolsDialog as filterlidar_dialog
        dialog = filterlidar_dialog(self.iface)
        dialog.exec_()

    # stima

    def selvar(self):
        from stim_selvar import STEMToolsDialog as selvar_dialog
        dialog = selvar_dialog(self.iface)
        dialog.exec_()

    def stimlim(self):
        from stim_linear import STEMToolsDialog as stimlim_dialog
        dialog = stimlim_dialog(self.iface)
        dialog.exec_()

    def svr(self):
        from stim_svr import STEMToolsDialog as svr_dialog
        dialog = svr_dialog(self.iface)
        dialog.exec_()

    # accuratezza

    def accuaccu(self):
        from post_accu import STEMToolsDialog as accu_dialog
        dialog = accu_dialog(self.iface)
        dialog.exec_()

    def accukfold(self):
        from post_kfold import STEMToolsDialog as kfold_dialog
        dialog = kfold_dialog(self.iface)
        dialog.exec_()

    def areeaggr(self):
        from post_aggraree import STEMToolsDialog as areeaggr_dialog
        dialog = areeaggr_dialog(self.iface)
        dialog.exec_()

    def bosco(self):
        from bosco import STEMToolsDialog as bosco_dialog
        dialog = bosco_dialog(self.iface)
        dialog.exec_()

    def settings(self):
        dialog = SettingsDialog(self.iface.mainWindow(), self.iface)
        dialog.exec_()
