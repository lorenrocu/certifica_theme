# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)
_logger.warning('=== CERTIFICA STOCK: LOADING MODELS DIRECTORY ===')

# Importar todos los modelos personalizados
from . import res_partner
from . import base_vat_override
from . import l10n_latam_override
from . import vat_validation_override
from . import vat_monkey_patch
from . import disable_validations
from . import product_stock