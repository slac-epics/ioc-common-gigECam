TOP=../..
include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE

#----------------------------------------------------
# Create and install (or just install)
# databases, templates, substitutions like this
DB += iocAdmin.db
DB += evrPmc230.db

# Create and install Camera DB Files
DB += prosilica.db

# Create and install plugin DB Files
DB += pluginBinnedImage.db
DB += pluginColorConvert.db
DB += pluginFileMPEG.db
DB += pluginHDF5.db
DB += pluginImage.db
DB += pluginJPEG.db
DB += pluginMagick.db
DB += pluginMJPG.db
DB += pluginNetCDF.db
DB += pluginNexus.db
DB += pluginOverlay.db
DB += pluginProcess.db
DB += pluginROI.db
DB += pluginStats.db
DB += pluginTIFF.db
DB += pluginThumbnail.db
DB += pluginTransform.db

DB_INSTALLS += $(AUTOSAVE)/db/save_restoreStatus.db
DB_INSTALLS += prosilica_gige.template

#----------------------------------------------------
# Create and install (or just install)
# Archive files, templates, substitutions like this
#
ARCHIVE += gige-ioc.archive
ARCHIVE += gige-camera.tpl-arch

#----------------------------------------------------
# Create and install (or just install)
# Autosave request files, templates, substitutions like this
#
REQ += gige-ioc.req
REQ += gige-camera.tpl-req

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

