""" implementation of the attribute enumerations
"""

#pylint: disable=line-too-long

import enum

class AttributeIdEnums(enum.IntEnum):
    """ implementation of the attribute enumerations
    """

    PRIMARY_KEY = 1
    """ PrimaryKey (please do not rename it) """

    FILE_ID = 4
    """ File ID (drawing file number/name) """

    ALLRIGHT_COMP_ID = 10
    """ Unique component ID + file ID + component code """

    COMPONENT_ID = 12
    """ Component ID """

    PROJECT_STATUS = 15
    """ Project status """

    ATTRIBUTE_VALUE = 17
    """ Attribute value - data record """

    NAMENUMBER_OF_STAIR_COMPONENT = 18
    """ Name/number of stair component """

    NUMBER_OF_STEP = 19
    """ Number of step """

    USER_NAME = 20
    """ Username (login) """

    BOTANICAL_NAME = 22
    """ Bruns: botanical name """

    PLANT_SPECIES = 23
    """ Plants: species """

    PLANTS_SHAPE = 24
    """ Plants: shape """

    PLANTS_GROWTH = 25
    """ Plants: growth """

    PLANTS_QUALITY = 26
    """ Plants: quality """

    BRUNS_PRICE = 27
    """ Plants: price """

    PLANT_GROUP = 28
    """ Plant group """

    PLANTS_GERMAN_NAME = 29
    """ Plants: German name """

    PLANTS_MATCH_CODE = 30
    """ Plants: match code """

    DIAMETER_OF_TRUNK = 31
    """ Diameter of trunk """

    DIAMETER_OF_TOP = 32
    """ Diameter of top """

    RETAIN = 33
    """ retain """

    PLANT = 34
    """ plant """

    CLEAR = 35
    """ fell/clear """

    BRUNS_PRICE_FOR_TEN_OR_MORE_PLANTS = 36
    """ Plants: price for ten or more pieces """

    BRUNS_PRICE_FOR_50_OR_MORE_PLANTS = 37
    """ Plants: price for 50 or more pieces """

    AGE = 40
    """ Age """

    VITALITY = 41
    """ Vitality """

    DATE_ADDED = 42
    """ Date added """

    HIGHLIGHT = 43
    """ Marking type """

    SOLID_2D_INTERACTION = 45
    """ Solids 2D interaction """

    NBS_REFERENCE_DESCRIPTION = 46
    """ Categorization - NBS Reference Description """

    CSI_MASTER_FORMAT_CODE = 47
    """ Classification - CSI MasterFormat Code """

    CSI_MASTER_FORMAT_TITLE = 48
    """ classification - CSI MasterFormat Title """

    STATUS = 49
    """ IFC: Status """

    IN_HIERARCHY = 53
    """ Level 1 in hierarchy """

    PARTIAL_AREA_FORMAT = 54
    """ Returns user-defined format string for reports """

    CSI_UNI_FORMAT_II_CODE = 56
    """ Categorization - CSI UniFormat II Code """

    CSI_UNI_FORMAT_II_TITLE = 57
    """ Categorization - CSI UniFormat II Title """

    BIMPLUS_LAYER = 67
    """ BimPlus Layer (Discipline) """

    FLOOR_AREA = 68
    """ Floor area depending on current setting """

    E_MAIL = 69
    """ Office: email address """

    LOGO = 70
    """ Company logo: default in $ETC/Allplan_Logo_204_77.png """

    INHERITANCE = 72

    UNIT_1 = 73

    REVEAL_DEPTH = 74
    """ Reveal depth """

    CALCULATION_RULE = 75
    """ Calculation rule """

    OBJECT_FILTER = 76
    """ Object filter """

    FILTER_BY_SURROUNDING_ELEMENTS_SUBTR = 77
    """ Filters by surrounding elements to be subtracted """

    FORMWORK_AREA = 78
    """ Formwork area """

    REVEAL_ANALYSIS = 79
    """ Reveal analysis """

    VOB_LENGTH = 80
    """ Trade-dependent length calculation """

    VOB_AREA = 81
    """ Trade-dependent area calculation """

    VOB_VOLUME = 82
    """ Trade-dependent volume calculation """

    CODE_TEXT = 83
    """ Code text for TAI program assignment """

    COLUMN_PROJECTING = 84
    """ Projecting column """

    COLUMN_FLUSH_WITH_WALL = 85
    """ Column flush with wall """

    VOLUME_DIN277 = 86
    """ Volume in accordance with DIN277 """

    SVG_MAP = 87
    """ SVG map: 2D geodetic info """

    NUMBER_OF_RISER = 88
    """ Stair: number of rises """

    RISE = 89
    """ Stair: rise """

    TREAD_LENGTH = 90
    """ Stair: tread run """

    NUMBER_INSIDE_CORNERS = 91
    """ Number of inside corners """

    NUMBER_OUTSIDE_CORNERS = 92
    """ Number of outside corners """

    BASE_AREA_ACCORDING_TO_DIN277 = 93
    """ Base area in accordance with DIN277 """

    DYN_UNIT_PRICE = 95
    """ Dynamic unit price """

    DYN_MATERIAL = 96
    """ Dynamic material """

    BOTTOM = 97
    """ Bottom level of component """

    COMPONENT_TOP_LEVEL = 98
    """ Top level of component """

    NET_QUANTITY = 99
    """ Net quantity """

    VOB_QUANTITY = 100
    """ VOB qantity """

    RADIUS = 107
    """ Radius """

    PRIORITY = 110
    """ Priority """

    BOTTOM_LEVEL = 112
    """ Applied to openings, this attribute returns the offset to the bottom level of the wall; otherwise, this attribute returns the bottom level """

    TOP_LEVEL = 113
    """ Top level """

    CALCULATION_MODE = 120
    """ Calculation mode """

    RISE_TOP = 127
    """ Rise at top """

    RISE_BOTTOM = 129
    """ Rise at bottom """

    OFFSET_LEFT = 131
    """ Offset on the right """

    OFFSET_RIGHT = 132
    """ Offset on the left """

    LAYER = 141
    """ Layer """

    X_COORDINATE = 163
    """ x-coordinate """

    Y_COORDINATE = 164
    """ y-coordinate """

    Z_COORDINATE = 165
    """ z-coordinate """

    OFFSET_TOP = 167
    """ Offset at the top """

    COMPONENT_DEPTH = 179
    """ Component depth """

    FLOOR_AREA_LESS_PERCENTAGE = 193
    """ Floor area (unfinished dimensions including amount to subtract) """

    MARK_NUMBER = 194
    """ Mark number """

    CATALOG_BRANCH = 195
    """ Catalog branch """

    FLOOR_AREA_UNFINISHED_DIMENSIONS = 196
    """ Floor area (unfinished dimensions) """

    FLOOR_AREA_FINISHED_DIMENSIONS = 197
    """ Floor area (finished dimensions) """

    ABSOLUTE_LENGTH = 198
    """ Absolute length """

    ABSOLUTE_THICKNESS = 199
    """ Absolute thickness """

    QUANTITY = 201
    """ Quantity """

    UNIT = 202
    """ Unit """

    UNIT_PRICE = 203
    """ Unit price """

    ABSOLUTE_HEIGHT = 204
    """ Maximum height of architectural components """

    SEQUENCE_NUMBER = 206
    """ Serial number """

    SHORT_TEXT = 207
    """ Short text """

    FULL_TEXT = 208
    """ Full text """

    TRADE = 209
    """ Trade """

    LAYER_NUMBER = 210
    """ Layer number """

    LAYER_THICKNESS = 211
    """ Layer thickness """

    REVEAL_AREA = 212
    """ Reveal on the inside; analysis: reveal area """

    REVEAL_LENGTH = 213
    """ Reveal on the outside; analysis: reveal length """

    ARCHITECTURAL_COMPONENT = 214
    """ Architectural component number """

    PIECE = 215
    """ Piece """

    V6 = 216
    """ V6 - V9 --&gt; smart symbol """

    V7 = 217
    """ V6 - V9 --&gt; smart symbol """

    V8 = 218
    """ V6 - V9 --&gt; smart symbol """

    V9 = 219
    """ V6 - V9 --&gt; smart symbol """

    LENGTH = 220
    """ Length """

    THICKNESS = 221
    """ Thickness """

    HEIGHT = 222
    """ Mean height (volume, base area) """

    VOLUME = 223
    """ Volume """

    BASE_AREA = 224
    """ Base area """

    DIMENSIONS = 225
    """ Dimensions """

    NET_VOLUME = 226
    """ Net volume """

    LESS_VOLUME = 227
    """ Volume to be subtracted """

    PERIMETER = 228
    """ Perimeter """

    AREA = 229
    """ Area """

    FACTOR = 230
    """ Factor """

    ROOM_ENCLOSURE = 231
    """ DIN277: room enclosure """

    AREA_TYPE_277 = 232
    """ DIN277: area type """

    AREA_TYPE_FLOOR_SPACE = 233
    """ Area type: floor area """

    BAU_NVO_FA = 234
    """ BauNVO: story included in calculation of base area """

    OCCUPANCY_TYPE_DIN277 = 235
    """ DIN277: occupancy type """

    LOCAL_CODE_ROOM_NAME = 236
    """ Local code: room name """

    LOCAL_CODE_SUBROOM_NUMBER = 237
    """ Local code: number of subroom """

    CONCRETING_SECTION = 238
    """ Concreting section """

    INITIALCLOSING_FORM = 239
    """ Formwork closer """

    LONG_NAME_FOR_FORMWORK = 240
    """ Full name of formwork """

    ARTICLE_NUMBER = 241
    """ Article number """

    EFA = 242
    """ DIN277: EFA """

    ERC = 243
    """ DIN277: ERC """

    GFA = 244
    """ DIN277: GFA """

    GRV = 245
    """ DIN277: GRV """

    LOCAL_CODE_STORY_NAME = 246
    """ Local code: story name """

    LOCAL_CODE_SUBSTORY_NUMBER = 247
    """ Local code: substory number """

    NRA = 248
    """ DIN277_2016: net room area """

    NRV = 249
    """ DIN277: NRV """

    BAU_NVO_FS = 250
    """ BauNVO: story included in calculation of story area """

    SPACE_BELOW_STAIRS_FLR_SPC_ONLY_GT_2M = 251
    """ Space below stair included in floor area &gt; 2.0 m """

    FACTOR_FLOOR_AREA_ROOM = 264
    """ Room factor: floor area """

    FACTOR_277 = 266
    """ DIN277: factor 277 """

    OFFSET_TO_PARAPET = 269
    """ Smart window sill symbols: offset to parapet """

    RADIUS_FLUE = 270
    """ Diameter of flue 1 """

    FLUE_WIDTH = 271
    """ Width of flue 1 """

    FLUE_THICKNESS = 272
    """ Thickness of flue 1 """

    RADIUS_FLUE2 = 273
    """ Diameter of flue 2 """

    WIDTH_FLUE2 = 274
    """ Width of flue 2 """

    THICKNESS_FLUE2 = 275
    """ Thickness of flue 2 """

    WIDTH_VENTSTACK = 276
    """ Width of ventilation stack 1 """

    DEPTH_VENTSTACK = 277
    """ Thickness of ventilation stack 1 """

    WIDTH_VENTSTACK2 = 278
    """ Width of ventilation stack 2 """

    THICKNESS_VENTSTACK2 = 279
    """ Thickness of ventilation stack 2 """

    INVENTORY_NUMBER_FORMWORK = 281
    """ Inventory number of formwork element """

    FORMWORK_ELEMENT_WEIGHT = 282
    """ Weight of formwork element """

    FORMWORK_ELEMENT_AREA = 283
    """ Area of formwork element """

    FORMWORK_ELEMENT_VALUE_NEW = 284
    """ New value of formwork element """

    SUPPLEMENT_FOR_FWK_ELEMENT = 285
    """ Supplement for formwork element """

    NOTE_FOR_FORMWORK_ELEMENT = 286
    """ Note for formwork element """

    ELEMENT_GROUP_FORMWORK = 287
    """ Element group for formwork element """

    NUMBER_IN_ELEMENT_PLAN = 288
    """ Number in element plan """

    COUNTRY = 289
    """ Project attribute: country """

    STATE = 290
    """ Project attribute: state """

    COST_GROUP_II = 291
    """ Cost group of level 2 """

    COST_GROUP_III = 292
    """ Cost group of level 3 """

    FLOOR_SURFACE = 293
    """ Floor surface """

    CEILING_SURFACE = 294
    """ Ceiling surface """

    VERTICAL_SURFACE = 295
    """ Vertical surface """

    MEAN_AREA = 296
    """ Mean area """

    PRICE_FACTOR = 297
    """ DIN276: price factor """

    ALLFA_COST_CENTER_ABBR__PATH_NAME = 301
    """ Allfa cost center (abbreviated path name) """

    TELEPHONE_NUMBER = 302
    """ Telephone number """

    ALLFA__ORGANIZAT__UNITABBR__PATH_NAME = 303
    """ Allfa organizational unit: abbreviated path name """

    EMPLOYEE_NAME = 304
    """ Employee name """

    PERSONNEL_NUMBER = 305
    """ Personnel number """

    ALLFA_ORGANIZATION_ABBR__NAME = 306
    """ Allfa organization (abbreviated name) """

    OBJECT_NUMBER = 307
    """ Object number """

    ALLFA_POSITION_NAME = 308
    """ Allfa position (description) """

    ALLFA_OCCUPANCY_NAME = 315
    """ Allfa occupancy (description) """

    ALLFA_CLEANING_CATEGORY_SHORT_DES__PATH = 316
    """ Allfa cleaning category: abbreviated path name """

    ALLFA_ORGANIZATION_NAME = 317
    """ Allfa organization (description) """

    ALLFA_ORGANIZATIONAL_UNIT_NAME = 318
    """ Allfa organizational unit (description) """

    ALLFA_POSITION_ABBR__NAME = 319
    """ Allfa position (abbreviated name) """

    ALLFA_EQUIPMENT_ABBR__NAME = 320
    """ Allfa equipment: abbreviated name """

    ALLFA_COST_CENTER_NAME = 321
    """ Allfa cost center (name) """

    ALLFA_OCCUPANCY_ABBR__PATH_NAME = 322
    """ Allfa occupancy type: abbreviated path name """

    ALLFA_ARTICLE_ABBR__PATH_NAME = 324
    """ Allfa article: abbreviated path name """

    ALLFA_ROOM_NAME = 327
    """ Allfa room (description) """

    RIDGE_LENGTH = 340
    """ Ridge length """

    ARRIS_LENGTH = 341
    """ Arris length """

    VALLEY_LENGTH = 342
    """ Valley length """

    EAVES_LENGTH = 343
    """ Eaves length """

    VERGE_LENGTH = 344
    """ Verge length """

    SMART_SYMBOL_HAS_A_TIMBER_FRAME = 358
    """ Smart symbol designer: smart symbol with wooden frame """

    BIT_SEQUENCE_LEAF_DINLEFT__DINRIGHT = 363
    """ Smart symbol designer: bit flags, leaf DINleft """

    FRAME_POSITION = 366
    """ Smart symbol designer: position of frame """

    ALLFA_CLEANING_CATEGORY_NAME = 367
    """ Allfa cleaning category (description) """

    PROJECT_AVAILABILITY = 368
    """ Project availability """

    NOTE_GENERAL = 372

    CHECKER_NAME = 374
    """ Person who checks the layout """

    LAYOUT_FORMAT = 375

    SCALE = 376

    FILE_NAME_SYMBOL = 378
    """ Name of symbol file """

    NEXT__NAME_SYMBOL = 379
    """ Symbol name """

    POSITION_INSIDEOUTSIDE = 384
    """ Window sill: on the inside or outside """

    SPLAY = 385
    """ Window sill: splay """

    APPROVAL_DATE = 386
    """ Release date """

    CHECKER_DATE = 387
    """ Release date """

    CHECKER_NOTE = 388
    """ Checker """

    INDEX = 389
    """ Layout index """

    BLDG_PROPOSAL_COSTS_PER_M3 = 394
    """ Building cost per m3 """

    CHECKED_BY = 395
    """ Person who checks the layout """

    INDEX_CREATED_BY = 396
    """ Person who edits the layout """

    INDEX_DATE = 397
    """ Date of change """

    PERFORMANCE_PLANNING_STAGE = 398
    """ Service phase, planning phase """

    CITY_STREET = 399
    """ City and street """

    CONSTRUCTION_STAGE = 400
    """ Construction stage """

    CURRENT_DATE = 401
    """ Current date """

    CURRENT_TIME = 402
    """ Current time """

    COMPUTER = 403
    """ Computer name """

    CURRENCY = 404
    """ Current currency """

    PROJECT_NAME = 405
    """ Project name """

    BLDG_PROPOSAL_STRUCTURE = 406
    """ Cost of unfinished structure for lists in building proposal """

    BLDG_PROPOSAL_FINISHING_COSTS = 407
    """ Cost of finished structure for lists in building proposal """

    FILESET_NUMBER = 408
    """ Fileset number """

    FILESET_NAME = 409
    """ Fileset name """

    OFFICE_NAME = 410
    """ Customer name, lines 1 - 2 """

    OFFICE_ADDRESS = 411
    """ Customer name, lines 1 - 2 """

    ENGINEERING_PROJECT = 413
    """ Engineering project """

    CONTRACT_SECTION = 414
    """ Lot """

    LAYOUT_VERSION = 415
    """ Layout version """

    FILE_NAME = 416
    """ File name """

    SEQUENCE_NAME = 417
    """ Sequence name """

    SL_CONSTRUCTION_PROJECT = 418
    """ Construction project """

    COMPONENT = 419
    """ Component """

    STEEL_LIST_NUMBER = 420
    """ Steel list number as saved in drawing file header  """

    NAME_OF_CROSS_SECTION_CATALOG = 421
    """ Name of cross-section catalog """

    STEEL_GRADE_OF_CROSS_SECTION_CATALOG = 422
    """ Steel grade of cross-section catalog """

    NUMBER_OF_TIMES = 423
    """ Number of instances """

    STEEL_STRENGTH_CATEGORY = 424
    """ Steel strength class """

    DRAWING_FILE_NAME = 425
    """ Drawing file name """

    INDEX_TYPE = 426

    DOOR_SWING = 427
    """ Direction of door swing """

    APPROVAL_NAME = 428
    """ Approval name """

    FILE_SIZE = 429
    """ Size plus unit (character) """

    HIERARCHIC_CODE = 430
    """ Hierarchical code """

    OWNER = 431
    """ Owner """

    CREATED_ON = 432
    """ Date of creation """

    DATE_OF_CHANGE = 433
    """ Date of change """

    DISPLAY_MODE = 434
    """ Display mode """

    INDEX_OLD = 435
    """ Layout index in V2011 and earlier versions """

    FILE_SIZE_BYTES = 436
    """ File size in bytes """

    HIDDENSECTION = 437
    """ Hidden/section """

    LAYOUT_TYPE = 438
    """ Layout type """

    LAYOUT_DESCRIPTION = 439
    """ Layout description """

    NUMBER_CHANGES = 440
    """
 """

    WRITE_PERMISSION = 441
    """ Write permission """

    LAYOUT_RELEASE_DATE = 443
    """ Release date """

    CHECKER = 444
    """ Checker """

    LAYOUT_NAME = 445
    """ Full layout name """

    LAYOUT_NUMBER = 446
    """ Layout number """

    INDEX_NOTE = 447
    """ Change notice """

    REFERENCE_SCALE = 448
    """ Reference scale """

    RELEASE = 449
    """ Program version, release """

    TOPOLOGY_STRUCTURE = 450
    """ Building topology, structure """

    TOPOLOGY_BUILDING = 451
    """ Building topology, building """

    TOPOLOGY_STORY = 452
    """ Building topology, floor level """

    TOPOLOGY_ROOM = 453
    """ Topology, room """

    SELECTION_CONDITION_5 = 454
    """ Selection condition 5 """

    SELECTION_CONDITION_6 = 455
    """ Selection condition 6 """

    SELECTION_CONDITION_7 = 456
    """ Selection condition 7 """

    SELECTION_CONDITION_8 = 457
    """ Selection condition 8 """

    SELECTION_CONDITION_9 = 458
    """ Selection condition 9 """

    SELECTION_CONDITION_10 = 459
    """ Selection condition 10 """

    CLIENT = 460
    """ Client """

    OCCUPANTS = 461
    """ Occupant """

    BUILDING_TYPE = 462
    """ Building type """

    TYPE_OF_CONSTRUCTION_LOAD_BEARING_STRUCTURE = 463
    """ Type of construction, load-bearing structure """

    CONSTRUCTION_VOLUME = 464
    """ Project attribute: construction volume in € """

    GROSS_FLOOR_AREA = 465
    """ Project attribute: gross floor area """

    FLOOR_AREA_RATIO = 466
    """ Project attribute: floor area ratio """

    USABLE_FLOOR_AREA = 467
    """ Project attribute: usable floor area """

    NO__OF_FLOOR_LEVELS = 468
    """ Project attribute: number of floor levels """

    NO__OF_RESIDENTIAL_UNITS = 469
    """ Project attribute: number of residential units """

    RESIDENTIAL_BUILDING_DEVELOPMENT = 470
    """ Residential building development """

    OFFICE_SPACE = 471
    """ Office space """

    OFFICE_DEVELOPMENT = 472
    """ Office development """

    YEAR_OF_COMPLETION = 473
    """ Year of completion """

    LOCATION_PLOT = 474
    """ Location, plot """

    AUTHORIZING_AGENCY = 475
    """ Approving authority """

    DATE_APPROVED = 476
    """ Date of approval """

    LOT = 477
    """ Lot """

    PROJECT_MANAGER = 478
    """ Project manager """

    ARCHITECT = 479
    """ Architect """

    STRUCTURAL_ANALYSIS = 480
    """ Structural analysis """

    LAYOUT_CREATED_BY = 481
    """ Person who creates the layout """

    ELECTRICAL_INSTALLATION = 482
    """ Electrical installations """

    HEATING = 483
    """ Heating """

    VENTILATION = 484
    """ Ventilation """

    SANITARY_FACILITIES = 485
    """ Sanitary facilities """

    BUILDING_PHYSICS = 486
    """ Building physics """

    ARCHITECTURAL_ACOUSTICS = 487
    """ Architectural acoustics """

    OPEN_AREA_PLANNING = 488
    """ Open area planning """

    INFRASTRUCTURE_PLANNING = 489
    """ Infrastructure planning """

    INTERIOR_DESIGN = 490
    """ Interior design """

    CONSTRUCTION_SUPERVISION = 491
    """ Construction supervision """

    PROJECT_MANAGEMENT = 492
    """ Project management """

    COST_CONTROL = 493
    """ Cost controlling """

    PRECAST_FACTORY = 494
    """ Precast factory """

    SHORT_NAME_FOR_STEEL_GRADE = 495
    """ Steel grade, short name """

    NO__OF_CROSS_SECTION_CATALOG = 496
    """ Number of cross-section catalog """

    LESS_PERCENTAGE_FLOOR_AREA = 497
    """ Former floor area factor; percentage to be subtracted from floor area  """

    OBJECT_NAME = 498
    """ Object name """

    PAGE_NUMBER = 499
    """ Page """

    BLDG_PROPOSAL_PLOT_AREA = 500
    """ Plot area for lists in building proposal """

    TEXT1 = 501
    """ Text1 """

    TEXT2 = 502
    """ Text2 """

    TEXT3 = 503
    """ Text3 """

    TEXT4 = 504
    """ Text4 """

    TEXT5 = 505
    """ Text5 """

    FUNCTION = 506
    """ Function """

    NAME = 507
    """ Name """

    MATERIAL = 508
    """ Material """

    FILE_NUMBER_IDAT = 511
    """ File number (idat) """

    DRAWING_FILE_NUMBER_ITBNR = 512
    """ File number (itbnr) """

    REINFORCEMENT_PERCENTAGE = 514
    """ Reinforcement percentage """

    SEGMENT_NUMBER = 515
    """ Segment number """

    DOCUMENT_UUID = 523
    """ UUID of document, layout or project    """

    LINE_NUMBER = 532
    """ Table analysis """

    PLUGIN_NAME = 538
    """ Plugin name """

    PLUGIN_OBJECT_NAME = 539
    """ Plugin object name """

    BUILDABLE_AREA = 548
    """ Project attribute: area available for building """

    MAXIMUM_BUILDING_HEIGHT = 549
    """ Project attribute: maximum building height """

    GROSS_PLOT_AREA = 550
    """ Project attribute: gross plot area """

    CODE_OCCUPANCY = 551
    """ Urban planning: land-use type """

    BUILDING_METHOD = 552
    """ Urban planning: construction method """

    MAX__SITE_AREA_RATIO = 553
    """ Urban planning: maximum site area ratio """

    NUMBER_OF_PLOT = 554
    """ Urban planning: plot number """

    MAX__SITE_OCCUPANCY_INDEX = 555
    """ Urban planning: maximum site occupancy index """

    MIN__FLOOR_AREA_RATIO = 556
    """ Urban planning: minimum floor area ratio """

    MAX__FLOOR_AREA_RATIO = 557
    """ Urban planning: maximum floor area ratio """

    MIN__NO__OF_FULL_STORIES = 558
    """ Urban planning: minimum number of full stories """

    MAX__NO__OF_FULL_STORIES = 559
    """ Urban planning: maximum number of full stories """

    ROOF_PITCH_AND_SHAPE = 560
    """ Urban planning: roof pitch and roof shape """

    DRAWING_SYMBOL_GROUP = 561
    """ Urban planning: drawing symbol group """

    DRAWING_SYMBOL_REGULATIONS = 562
    """ Drawing symbol """

    LEGAL_BASIS_FOR_GROUP = 563
    """ Legal basis for drawing symbol group """

    LEGAL_BASIS_FOR_REGULATION = 564
    """ Legal basis for drawing symbol regulations """

    NUMBER_OF_FULL_STORIES = 565
    """ Number of full stories """

    BUILDING_STORY_SAFA = 566
    """ Urban planning: consider floor area ratio and site occupancy index (yes, no) """

    NUMBER_OF_RESIDENTIAL_UNITS = 567
    """ Number of residential units """

    NUMBER_OF_TOP_FLOORS = 568
    """ Number of upper floors """

    PARKING_SPACE_FOR_N_CARS = 569
    """ Parking space for n cars """

    ARCHITECTURE_MATERIAL = 570
    """ Architectural material """

    STRUCTURAL_ANALYSIS_MATERIAL = 571
    """ Structural analysis material """

    LOAD_BEARING = 573
    """ Structural behavior, , BuildingSmart: load bearing """

    BUILDING_PHYSICS_MATERIAL = 574
    """ Building physics material  """

    PRODUCTION_TYPE = 575
    """ Production type """

    MEAN_SEA_LEVEL = 585
    """ Project attribute: heights above mean sea level """

    TOPOLOGY_SITE = 586
    """ Building topology, site """

    TOPOLOGY_STORY_REGION = 587
    """ Building topology, substory """

    TOPOLOGY_ANY_STRUCTURAL_LEVEL = 588
    """ Building topology, any structural level """

    TOPOLOGY_ENTIRE_HIERARCHY = 589
    """ Building topology, entire hierarchy including all nodes """

    NUMBER_OF_INTERSECTED_TILES = 590
    """ Smart fit: number of intersected tiles """

    NUMBER_OF_WHOLE_TILES = 591
    """ Smart fit: number of whole tiles """

    SURFACE_COMPRISED_BY_INTERSECTED_TILES = 592
    """ Smart fit: area covered by intersected tiles """

    SURFACE_COMPRISED_BY_WHOLE_TILES = 593
    """ Smart fit: area covered by whole tiles """

    TOTAL_PRICE = 594
    """ Total price """

    LEFT_HAUNCH = 595
    """ Foundations, left haunch """

    RIGHT_HAUNCH = 596
    """ Foundations, right haunch """

    FRONT_HAUNCH = 597
    """ Foundations, front haunch """

    REAR_HAUNCH = 598
    """ Rear haunch """

    VTB_INFO = 599
    """ VTB 19 """

    STEPCHAMFER_WIDTH = 601
    """ Foundations, width of step chamfer """

    STEPCHAMFER_HEIGHT = 602
    """ Foundations, height of step chamfer """

    STEP_BOUNCE = 603
    """ Foundations, step chamfer """

    STEPCHAMFER_ECCENTRICITY = 605
    """ Foundations, eccentricity of step chamfer """

    CENTER_OF_GRAVITY_X = 612
    """ X center of gravity """

    CENTER_OF_GRAVITY_Y = 613
    """ Y center of gravity """

    CENTER_OF_GRAVITY_Z = 614
    """ Z center of gravity """

    DEFAULT_PLANE_BL = 615
    """ Bottom level of default plane """

    DEFAULT_PLANE_TL = 616
    """ Top level of default plane """

    NOI_ID = 617
    """ NOI ID  """

    IS_EXTERNAL = 618
    """ Classification -&gt; Ifc exterior component """

    GLASS_TYPE = 619
    """ Glass type """

    SHADING_COEFFICIENT = 620
    """ Shading Coefficient """

    GLAZING_AREA_FRACTION_CONSIDER = 621
    """ Consider GlazingAreaFraction for Smt reports """

    ABSORPTION_COEFFICIENT_HEAT_INSIDE = 622
    """ Absorption coefficient of heat, inside """

    ABSORPTION_COEFFICIENT_HEAT_OUTSIDE = 623
    """ Absorption coefficient of heat, outside """

    TEMPERATURE = 624
    """ Temperature """

    ROOM_ZONE_ACC__TO_DIN_18599 = 625
    """ Room zone (in accordance with DIN 18599) """

    LIGHT_REFLECTION_COEFFICIENT_OF_CEILING = 626
    """ Light reflection coefficient """

    GROUND = 645
    """ Ground """

    LAMBDA_VALUE = 657
    """ Lambda value (thermal conductivity nominal value λ) """

    IFC_ID = 683
    """ IFC ID """

    IFC_ENTITY = 684
    """ IFC object type """

    ASSIGNMENT_TO_FIRE_COMPARTMENT = 685
    """ Assignment to fire compartment """

    RAFTER_PARAMETERS = 689

    SWITCH_B_IS_FS = 690

    SWITCH_TF_IS_FS = 691

    MIN_HEIGHT_SO_THAT_FS = 692

    HEIGHT_ABOVE_TERRAIN_SO_THAT_B_IS_FS = 693

    BUILDING_ID = 696
    """ Project attribute: building ID """

    PRODUCT_MANUFACTURER = 708
    """ MEP: manufactrurer """

    WEIGHT = 721
    """ Weight """

    SURFACE = 722
    """ Surface """

    BAR_LENGTH_BS_8666 = 740
    """ Bending dimensions (length of each bar) BS 8666:2005 """

    BENDING_DIMENSIONS_BS_86662005_A_E = 741
    """ Bending dimensions (a """

    DEFAULT_PATH_FOLDER = 742
    """ Main nodes of the Allplan default paths (etc,std,...) """

    LAYOUT_STRUCTURE_ENTIRE_HIERARCHY = 743
    """ Entire layout structure """

    LAYOUT_STRUCTURE_SUPERORDINATE_NODE = 744
    """ Superordinate node of the layout structure """

    PROJECT_TEMPLATE = 747
    """ Type of project template """

    SCHEDULE_OUTPUT___GROSS_WEIGHTNET_WEIGHT = 750
    """ Gross weight and net weight """

    MESH_NAME = 751
    """ Mesh identifier """

    LONGITUDINAL_CONCRETE_OVERLAP_M = 752
    """ Longitudinal mesh overlap """

    TRANSVERSE_CONCRETE_OVERLAP_M = 753
    """ Transverse mesh overlap """

    MAX__LONGITUDINAL_AS = 754
    """ Maximum value for As longitudinal """

    MAX__TRANSVERSE_AS = 755
    """ Maximum value for As transverse """

    WEIGHT_OF_MESHBAR = 756
    """ Weight of one mesh or bar """

    MESH_OR_BAR_LENGTH_SINGLE = 757
    """ Length of one mesh or bar """

    WIDTH = 758
    """ Width """

    DIAMETER = 759
    """ Diameter """

    TOTAL_LENGTH = 760
    """ Total length [m] """

    COMMENT_ON_BAR_X_SECTION_CATALOG = 761
    """ Comment on bar cross-section catalog """

    BENDING_DIMENSIONS_ISO_4066_A_E = 762
    """ Bending dimensions (a """

    BAR_SHAPE_KEY_ISO_4066 = 763
    """ Bar shape key ISO4066 """

    TYPE = 764
    """ Type """

    TOTAL_WEIGHT = 765
    """ Total weight """

    NO__OF_WWMREINFORCING_BARS = 766
    """ Number of meshes or reinforcing bars """

    WWMREINF__BAR_MARKS = 767
    """ Mark number of meshes or reinforcing bars """

    BAR_SPACING___LONGITUDINAL_MM = 768
    """ Bar spacing, longitudinal """

    BAR_SPACING___TRANSVERSE_MM = 769
    """ Bar spacing, transverse """

    INSIDE_DIA__DS1_LONGITUDINAL = 770
    """ Inside diameter ds1 longitudinal """

    INSIDE_DIA__DS3_TRANSVERSE = 771
    """ Inside diameter ds3 transverse """

    DM_EDGE_DS2_LONGIT = 772
    """ Edge diameter ds2 longitudinal """

    EDGE_DIAMETER_DS4_TRANSVERSE = 773
    """ Edge diameter ds4 transverse """

    NUMBER___LEFT_EDGE_NL = 774
    """ Number of bars, left edge nl """

    NUMBER___RIGHT_EDGE_NR = 775
    """ Number of bars, right edge nr """

    NUMBER___START_EDGE_MA = 776
    """ Number of bars, start edge ma """

    NUMBER___END_EDGE_ME = 777
    """ Number of bars, end edge me """

    DS1_DOUBLE_BAR_OR_SECONDARY = 778
    """ Double bar char*1 "d" only for ds1 """

    EXCESS___START_OF_MESH_UE1 = 779
    """ Projection at start Ue1 """

    EXCESS___END_OF_MESH_UE2 = 780
    """ Projection at end Ue2 """

    EXCESS___LEFT_UE3 = 781
    """ Projection on the left Ue3 """

    EXCESS___RIGHT_UE4 = 782
    """ Projection on the right Ue4 """

    OFFSET_SHORT_BARS_AK = 783
    """ Length as far as short bar ak """

    LENGTH_OF_SHORT_BARS_LK = 784
    """ Length of short bar lk """

    DIAMETERMESH_NAME = 785
    """ Diameter, mesh identifier """

    BAR_SHAPE_BS_8666 = 786
    """ Bar shape key BS 8666 """

    MESH_SHAPE = 787
    """ Mesh shape, planar or bent """

    VERSION = 789
    """ Version """

    MARK_SPACING_M = 790
    """ Mark spacing [m]- string """

    MARK_SPACING_CM = 791
    """ Mark spacing [cm] - string """

    FILTER_BY_REINF__PLACED_POLYGONALLY = 792
    """ Filter by reinforcement placed polygonally """

    FILTER_BY_REINF__BAR_ELE = 793
    """ Filter by bar reinforcement """

    MARK_NUMBER_WITH_INDEX_MESHESBARS = 795
    """ Mark number with index (meshes, bars) """

    LENGTH_CM_METERAGE = 796
    """ Length [cm] (per meter) - string """

    LENGTH_M_METERAGE = 797
    """ Length [m] (per meter) - string """

    VARIABLE_LENGTH_A_B_C___ = 798
    """ Variable length (a b c ...) """

    STRAIGHTBENT_UP_BARS = 799
    """ Bars, straight or bent """

    POINT_NUMBER = 800
    """ Point number """

    REFERENCE_HEIGHT = 801
    """ Reference height """

    DELTA_HEIGHT = 802
    """ Delta height """

    PRISM_NUMBER = 803
    """ Prism number """

    POINT_NUMBER_2 = 804
    """ Point number 2 """

    POINT_NUMBER_3 = 805
    """ Point number 3 """

    AVERAGE_HEIGHT = 806
    """ Mean height """

    ANALYSIS = 807
    """ Analysis """

    QUESTION_1 = 808
    """ Fixture question 1 """

    QUESTION_2 = 809
    """ Fixture question 2 """

    QUESTION_3 = 810
    """ Fixture question 3 """

    QUESTION_4 = 811
    """ Fixture question 4 """

    QUESTION_5 = 812
    """ Fixture question 5 """

    ANSWER_1 = 813
    """ Fixture answer 1 """

    ANSWER_2 = 814
    """ Fixture answer 2 """

    ANSWER_3 = 815
    """ Fixture answer 3 """

    ANSWER_4 = 816
    """ Fixture answer 4 """

    ANSWER_5 = 817
    """ Fixture answer 5 """

    FIXTURE_UNIT_1 = 818
    """ Fixture unit 1 """

    FIXTURE_UNIT_2 = 819
    """ Fixture unit 2 """

    FIXTURE_UNIT_3 = 820
    """ Fixture unit 3 """

    FIXTURE_UNIT_4 = 821
    """ Fixture unit 4 """

    FIXTURE_UNIT_5 = 822
    """ Fixture unit 5 """

    PLAN_TEXT = 823
    """ EB plan text """

    CONTRACT_NUMBER = 824
    """ Contract number """

    CONTRACTING_AUTHORITY = 825
    """ Contracting authority """

    CONSTRUCTION_PROJECT = 826
    """ Construction project """

    CONSTRUCTION_SITE = 827
    """ Construction site """

    EDITED_BY = 828
    """ Person who edits the layout """

    SLAB_OVER = 829
    """ Precast slab over """

    PROJECT_LAYOUT_NUMBER = 830
    """ Layout number """

    DELIVERY_ADDRESS = 831
    """ Delivery address """

    DELIVERY_STREET = 832
    """ Delivery street """

    DELIVERY_ZIP_CODECITY = 833
    """ Delivery ZIP code/city """

    INVOICE_ADDRESS = 834
    """ Invoice address """

    INVOICE_STREET = 835
    """ Invoice street """

    BUILDING_CONTRACTOR_ADDRESS = 836
    """ Building contractor, address """

    BUILDING_CONTRACTOR_STREET = 837
    """ Building contractor, street """

    BUILDING_CONTRACTOR_ZIP_CODECITY = 838
    """ Building contractor, ZIP code/city """

    CLIENT_ADDRESS = 839
    """ Client, address """

    CLIENT_STREET = 840
    """ Client, street """

    CLIENT_ZIP_CODECITY = 841
    """ Client, ZIP code/city """

    INVOICE_ZIP_CODECITY = 842
    """ Invoice, ZIP code/city """

    ALLFA_VALUE_01 = 843
    """ ALLFA: value 01 """

    ALLFA_VALUE_02 = 844
    """ ALLFA: value 02 """

    ALLFA_VALUE_03 = 845
    """ ALLFA: value 03 """

    ALLFA_VALUE_04 = 846
    """ ALLFA: value 04 """

    ALLFA_VALUE_05 = 847
    """ ALLFA: value 05 """

    ALLFA_VALUE_06 = 848
    """ ALLFA: value 06 """

    ALLFA_VALUE_07 = 849
    """ ALLFA: value 07 """

    ALLFA_VALUE_08 = 850
    """ ALLFA: value 08 """

    ALLFA_VALUE_09 = 851
    """ ALLFA: value 09 """

    ALLFA_VALUE_10 = 852
    """ ALLFA: value10 """

    ALLFA_VALUE_11 = 853
    """ ALLFA: value 11 """

    ALLFA_VALUE_12 = 854
    """ ALLFA: value 12 """

    ALLFA_VALUE_13 = 855
    """ ALLFA: value 13 """

    ALLFA_VALUE_14 = 856
    """ ALLFA: value 14 """

    ALLFA_VALUE_15 = 857
    """ ALLFA: value 15 """

    ALLFA_VALUE_16 = 858
    """ ALLFA: value 16 """

    ALLFA_VALUE_17 = 859
    """ ALLFA: value 17 """

    ALLFA_VALUE_18 = 860
    """ ALLFA: value 18 """

    ALLFA_VALUE_19 = 861
    """ ALLFA: value 19 """

    ALLFA_VALUE_20 = 862
    """ ALLFA: value 20 """

    ALLFA_FEATURE_01 = 863
    """ ALLFA: attribute 01 """

    ALLFA_FEATURE_02 = 864
    """ ALLFA: attribute 02 """

    ALLFA_FEATURE_03 = 865
    """ ALLFA: attribute 03 """

    ALLFA_FEATURE_04 = 866
    """ ALLFA: attribute 04 """

    ALLFA_FEATURE_05 = 867
    """ ALLFA: attribute 05 """

    ALLFA_FEATURE_06 = 868
    """ ALLFA: attribute 06 """

    ALLFA_FEATURE_07 = 869
    """ ALLFA: attribute 07 """

    ALLFA_FEATURE_08 = 870
    """ ALLFA: attribute 08 """

    ALLFA_FEATURE_09 = 871
    """ ALLFA: attribute 09 """

    ALLFA_FEATURE_10 = 872
    """ ALLFA: attribute 10 """

    ALLFA_FEATURE_11 = 873
    """ ALLFA: attribute 11 """

    ALLFA_FEATURE_12 = 874
    """ ALLFA: attribute 12 """

    ALLFA_FEATURE_13 = 875
    """ ALLFA: attribute 13 """

    ALLFA_FEATURE_14 = 876
    """ ALLFA: attribute 14 """

    ALLFA_FEATURE_15 = 877
    """ ALLFA: attribute 15 """

    ALLFA_FEATURE_16 = 878
    """ ALLFA: attribute 16 """

    ALLFA_FEATURE_17 = 879
    """ ALLFA: attribute 17 """

    ALLFA_FEATURE_18 = 880
    """ ALLFA: attribute 18 """

    ALLFA_FEATURE_19 = 881
    """ ALLFA: attribute 19 """

    ALLFA_FEATURE_20 = 882
    """ ALLFA: attribute 20 """

    CHANGE_PARAMETERS = 883
    """ Attributes of structural bearings """

    CLASS_NO_ = 885
    """ Fixtures, class number """

    STATION = 894
    """ Station """

    OFFSET_DTM = 895
    """ Offset """

    BULK_DENSITY = 897
    """ Bulk density """

    DELIVERY_UNIT_STATUS = 902
    """ Delivery unit status """

    MARK_NUMBER_OF_PRECAST_ELEMENT = 903
    """ Mark number of precast element """

    SLOPE = 909
    """ Slope """

    CUSTOMER_STREET = 910
    """ Customer, street """

    CUSTOMER_ZIP_CODECITY = 911
    """ Customer, ZIP code/city """

    ORDERER_ADDRESS = 912
    """ Orderer, address """

    ORDERER_STREET = 913
    """ Orderer, street """

    ORDERER_ZIP_CODECITY = 914
    """ Orderer, ZIP code/city """

    CHECKING_STRUCTURAL_ENGINEER_ADDRESS = 915
    """ Structural inspection engineer, address """

    CHECKING_STRUCTURAL_ENGINEER_STREET = 916
    """ Structural inspection engineer, street """

    CHECKING_STRUCTURAL_ENGINEER_ZIP_CODECITY = 917
    """ Structural inspection engineer, ZIP code/city """

    ARCHITECT_ADDRESS = 918
    """ Architect, address """

    ARCHITECT_STREET = 919
    """ Architect, street """

    ARCHITECT_ZIP_CODECITY = 920
    """ Architect, ZIP code/city """

    ADDRESS_OF_CONSTRUCTION_PROJECT = 921
    """ Construction project, address """

    CONSTRUCTION_PROJECT_STREET = 922
    """ Construction project, street """

    CONSTRUCTION_PROJECT_ZIP_CODECITY = 923
    """ Construction project, ZIP code/city """

    LAYOUTS = 924
    """ Layouts """

    CALCULATION_STANDARD = 925
    """ Calculation standard """

    SERVICE_CENTER = 926
    """ Service center """

    MOUNTING_HOOKS = 927
    """ Mounting anchors """

    STORAGE = 928
    """ Storage type """

    PRODUCTION_PLANT = 929
    """ Production plant """

    DELIVERY_YEAR = 930
    """ Delivery year """

    DELIVERY_WEEK = 931
    """ Delivery week """

    PRECAST_ELEMENT_TYPE = 932
    """ Element type of precast element """

    FIRE_RATING = 935
    """ Fire rating """

    PROJECT_NUMBER = 936
    """ Project number """

    SALES_ORGANIZATION = 937
    """ Sales organization """

    SALES_CHANNEL = 938
    """ Sales channel """

    DELIVERY_CONDITIONS = 939
    """ Delivery conditions """

    CLERK_TELEPHONE_NUMBER = 940
    """ Clerk, telephone number """

    CUSTOMER_TELEPHONE_NUMBER = 941
    """ Customer, telephone number """

    CUSTOMER_FAX_NUMBER = 942
    """ Customer, fax number """

    CUSTOMER_NUMBER = 943
    """ Customer, number """

    ORDERER_TELEPHONE_NUMBER = 944
    """ Customer, telephone number """

    ORDERER_FAX_NUMBER = 945
    """ Orderer, fax number """

    CHECKING_STRUCTURAL_ENGINEER_TELEPHONE_NUMBER = 946
    """ Structural inspection engineer, telephone number """

    CHECKING_STRUCTURAL_ENGINEER_FAX_NUMBER = 947
    """ Structural inspection engineer, fax number """

    STRUCTURAL_ENGINEER_NAME = 948
    """ Structural engineer, name """

    STRUCTURAL_ENGINEER_ADDRESS = 949
    """ Structural engineer, address """

    STRUCTURAL_ENGINEER_ZIP_CODECITY = 950
    """ Structural engineer, ZIP code/city """

    STRUCTURAL_ENGINEER_TELEPHONE_NUMBER = 951
    """ Structural engineer, telephone number """

    STRUCTURAL_ENGINEER_FAX_NUMBER = 952
    """ Structural engineer, fax number """

    ARCHITECT_TELEPHONE_NUMBER = 953
    """ Architect, telephone number """

    ARCHITECT_FAX_NUMBER = 954
    """ Architect, fax number """

    BUILDING_SITE_TELEPHONE_NUMBER = 955
    """ Building site, telephone number """

    BUILDING_SITE_FAX_NUMBER = 956
    """ Building site, fax number """

    PHASE_NUMBER = 957
    """ Phase number """

    PLACE_OF_MANUFACTURE = 958
    """ Place of manufacture """

    DEAD_LOAD = 959
    """ Dead load """

    VISIBLE_SIDE = 960
    """ Visible side """

    AREA_FACTOR = 961
    """ Area factor """

    LOAD_TRANSMISSION = 962
    """ Load transmission """

    INSERTION_DEPTH_1 = 963
    """ Insertion depth 1 """

    INSERTION_DEPTH_2 = 964
    """ Insertion depth 2 """

    OFFSET_TO_OPENING = 965
    """ Offset to opening """

    LONGITUDINAL_JOINT_WIDTH = 966
    """ Longitudinal joint width """

    TRANSVERSE_JOINT_WIDTH = 967
    """ Transverse joint width """

    REVEAL_ANCHOR_TYPE = 968
    """ Reveal anchor, left (top) or right (bottom) """

    FRAME_TYPE = 969
    """ Frame type """

    FRAME_WIDTH = 970
    """ Frame width """

    FRAME_HEIGHT = 971
    """ Frame height """

    SUPPORT_LENGTH_1 = 972
    """ Support length 1 """

    SUPPORT_LENGTH_2 = 973
    """ Support length 2 """

    SUPPORT_LENGTH_3 = 974
    """ Support length 3 """

    SUPPORT_LENGTH_4 = 975
    """ Support length 4 """

    FRAME_DIRECTION = 976
    """ Frame direction """

    AREA_TYPE = 980
    """ Envelope surfaces: area type """

    THERMAL_TRANSMITTANCE = 981
    """ Envelope surfaces: U-value """

    ENVELOPE_SURFACE_NAME = 982
    """ Envelope surfaces: name """

    ENVELOPE_SURFACE_ORIENTATION = 983
    """ Envelope surfaces: orientation """

    ENVELOPE_SURFACE_TYPE = 984
    """ Envelope surfaces: type """

    PROJECT = 985
    """ Envelope surfaces: project """

    HEAT_BRIDGE = 986
    """ Envelope surfaces: heat bridge """

    FACTOR_HEAT_REQUIREMENT = 987
    """ Envelope surfaces: factor """

    POSITION_OF_SURFACE = 988
    """ Envelope surfaces: position """

    COMPONENT_FILE = 989
    """ Envelope surfaces: component file """

    INPUT_AREA = 990
    """ Envelope surfaces: input area """

    PROJECT_DESCRIPTION = 991
    """ Project description (project attribute) """

    FACTORY = 992
    """ Factory (project attribute) """

    PART_OF_FACTORY = 993
    """ Part of factory (project attribute) """

    ALLFA_ROOM_ABBR__NAME = 994
    """ Allfa room (abbreviated name) """

    BAR_SHAPE_NEN_6146 = 996
    """ Bar shape key NEN 6146 """

    BENDING_DIMENSIONS_NEN_6146_A_F = 997
    """ Bending dimensions NEN 6146 [a-f] """

    NETHERLANDS_X1 = 998
    """ Netherlands: X1 """

    NETHERLANDS_Y1 = 999
    """ Netherlands: Y1 """

    GLASS_SURFACE = 1000
    """ Glazing area in m² """

    STEEL_GRADE_OF_CROSS_SECTION_CATALOG_WITHOUT_COUPLER = 1001
    """ Steel grade of cross-section catalog without couplers """

    COUPLER_TYPE = 1002
    """ Coupler type """

    COUPLER_DIAMETER = 1003
    """ Coupler diameter """

    CHECK_QUESTION_1 = 1008
    """ Check fixture question 1 """

    CHECK_QUESTION_2 = 1009
    """ Check fixture question 2 """

    CHECK_QUESTION_3 = 1010
    """ Check fixture question 3 """

    CHECK_QUESTION_4 = 1011
    """ Check fixture question 4 """

    CHECK_QUESTION__5 = 1012
    """ Check fixture question 5 """

    DIMENSION_STRING_INDEX = 1013
    """ Dimension string """

    CHAMFER___USER_ENTRY = 1014
    """ Chamfer: text for supplement """

    PALLET_SIDE___USER_ENTRY = 1015
    """ Pallet side: text for supplement """

    SMOOTH_FILLING_SIDE___USER_ENTRY = 1016
    """ Smooth filling side: text for supplement """

    FILLING_SIDE_SB___USER_ENTRY = 1017
    """ Filling side SB: text for supplement """

    STRUCTURE___USER_ENTRY = 1018
    """ Structure: text for supplement """

    WASHED_CONCRETE___USER_ENTRY = 1019
    """ Washed concrete: text for supplement """

    STRUCTURAL_POSITION___USER_ENTRY = 1020
    """ Structural position: text for supplement """

    ELEMENT_NAME = 1021
    """ Element name: text for supplement """

    FILESET_NAME___USER_ENTRY = 1022
    """ Fileset name: text for supplement """

    PROJECT_NAME___USER_ENTRY = 1023
    """ Project name: text for supplement """

    COMPONENT_SUPPLEMENT = 1024
    """ Component: text for supplement """

    FILESET_NUMBER___USER_ENTRY = 1025
    """ Fileset number: text for supplement """

    SUBTYPE = 1026
    """ Fixture subtype """

    CUSTOMER_ADDRESS = 1029
    """ Customer address (project attribute) """

    REFERENCE_ALLFA = 1030
    """ Associated with group for Unido (Allfa) """

    EXPOSURE_CLASS = 1031
    """ Exposure class """

    EXPOSURE_CLASS_VISIBLE = 1032
    """ Exposure class, visible """

    EXPOSURE_CLASS_INVISIBLE = 1033
    """ Exposure class, invisible """

    OFFSET_BOTTOM = 1035
    """ Offset at bottom """

    VARIABLE_SMART_FIXTURE_SYMBOL = 1038
    """ Variable smart fixture symbol """

    DIMENSON_TEXT = 1040
    """ Dimenson text """

    FF_STIRRUP_CAGES_FILTER = 1044
    """ FF stirrup cages, filter (is it a FF stirrup cage? 0/1) """

    FF_STIRRUP_CAGES_CODE = 1045
    """ FF stirrup cages, code (describing the stirrup cage, for example 2495M001/002/SC16) """

    FF_STIRRUP_CAGES_SORTING_NUMBER = 1046
    """ FF stirrup cages, sorting number = stack# * 1 000 000 000 + stack height*1 000 000 + element# *1000 + SC# """

    FF_STIRRUP_CAGES_REINFORCEMENT_TYPE_1 = 1047
    """ FF stirrup cages, filter by stock item """

    FF_STIRRUP_CAGES_REINFORCEMENT_TYPE_2 = 1048
    """ FF stirrup cages, filter by special reinforcement """

    TYPE_OF_INTERSECTION = 1049
    """ Type of intersection for FF reinforcement """

    FF_STIRRUP_CAGES_FILTER_FOR_PLACEMENT = 1050
    """ FF stirrup cages, filter by installation site = building site """

    REINFORCEMENT_TYPE_3_FILTER = 1051
    """ Reinforcement type 3, filter: returns all bars and stirrups with the installation site = building site """

    OFFSET_TO_BL_OF_PRECAST_ELEMENT = 1052
    """ Offset of fixture to bottom level of precast element """

    OFFSET_TO_TL_OF_PRECAST_ELEMENT = 1053
    """ Offset of fixture to top level of precast element """

    OFFSETS_TO_FF_REINFORCEMENT_COMPONENT = 1054
    """ Parts of FF reinforcement component """

    OFFSET_TO_BL_OF_ARCHITECTURAL_COMPONENT = 1055
    """ Offset of fixture to bottom level of architectural component """

    OFFSET_TO_TL_OF_ARCHITECTURAL_COMPONENT = 1056
    """ Offset of fixture to top level of architectural component """

    FACTORY_NUMBER = 1057
    """ Factory number """

    STEEL_WEIGHT = 1058
    """ Steel weight """

    FACING_THICKNESS_OF_VISIBLE_LEAF = 1059
    """ Facing thickness of visible leaf """

    FACING_THICKNESS_OF_INVISIBLE_LEAF = 1060
    """ Facing thickness of invisible leaf """

    CONCRETE_COVER_AT_BOTTOMINVISIBLE = 1061
    """ Concrete cover at bottom/invisible """

    CONCRETE_COVER_AT_TOPVISIBLE = 1062
    """ Concrete cover at top/visible """

    MATERIAL_OF_PRECAST_ELEMENT = 1063
    """ Material of precast element layer """

    CONCRETE_GRADE_OF_VISIBLE_LEAF = 1064
    """ Concrete grade of visible leaf --&gt; included for compatibility reasons only! Use 3201147 """

    CONCRETE_GRADE_OF_INVISIBLE_LEAF = 1065
    """ Concrete grade of invisible leaf --&gt; included for compatibility reasons only! Use 3201147 """

    CONCRETE_GRADE_OF_VISIBLE_OUTER_LEAF = 1066
    """ Concrete grade of visible outer leaf """

    CONCRETE_GRADE_OF_INVISIBLE_OUTER_LEAF = 1067
    """ Concrete grade of invisible outer leaf """

    VISIBLE_SURFACE = 1068
    """ Visible surface """

    INVISIBLE_SURFACE = 1069
    """ Invisible surface """

    REINFORCEMENT_TYPE = 1070
    """ Reinforcement type """

    VISIBLE_REINFORCEMENT_TYPE = 1071
    """ Visible reinforcement type """

    INVISIBLE_REINFORCEMENT_TYPE = 1072
    """ Invisible reinforcement type """

    ADDITIONAL_TEXT_FOR_MARK_NUMBER = 1073
    """ Additional text for mark number """

    MRK__NO__FOR_STACK_LIST = 1074
    """ Mark number for stack list (including sign) """

    PRECAST_TYPE = 1075
    """ Type of precast element """

    HEIGHT_OF_PRECAST_ELEMENT_IN_TRANSPORT_STACK = 1076
    """ Height of precast element in transport stack (including sign) """

    DIMENSIONS_OF_PRECAST_ELEMENT_M = 1077
    """ Dimensions of precast element [m] """

    THICKNESS_OF_PRECAST_ELEMENT_CM = 1078
    """ Thickness of precast element [cm] """

    STACK_NUMBER = 1079
    """ Stack number """

    SORTING_ID_OF_STACK_LIST = 1080
    """ Sorting ID of stack list """

    TOTAL_WEIGHT_OF_STIRRUP_CAGE = 1081
    """ Total weight of stirrup cage """

    ELEMENT_TYPE = 1082
    """ Element type - split type of element """

    CUSTOM_ATTRIBUTE_01 = 1083
    """ Precast elements: custom attribute 01 --&gt; included for compatibility reasons only! Use 1947! """

    CUSTOM_ATTRIBUTE_02 = 1084
    """ Precast elements: custom attribute 02 --&gt; included for compatibility reasons only! Use 1947! """

    CUSTOM_ATTRIBUTE_03 = 1085
    """ Precast elements: custom attribute 03 --&gt; included for compatibility reasons only! Use 1947! """

    CUSTOM_ATTRIBUTE_04 = 1086
    """ Precast elements: custom attribute 04 --&gt; included for compatibility reasons only! Use 1947! """

    CUSTOM_ATTRIBUTE_05 = 1087
    """ Precast elements: custom attribute 05 --&gt; included for compatibility reasons only! Use 1947! """

    PANEL_TYPE = 1088
    """ Panel type, name or description """

    GENERAL_CONSTRUCTION_PROJECT = 1091
    """ Construction project, general information """

    STORY = 1092
    """ Story """

    CONSTRUCTION_PROJECT_NAME = 1093
    """ Construction project, name """

    CONSTRUCTION_PROJECT_ADDRESS = 1094
    """ Construction project, address """

    ADDRESS_FOR_INVOICE = 1095
    """ Invoice address """

    FF_STIRRUP_CAGES_INSTALLATION_WORKS = 1096
    """ Installation site = factory (1 otherwise 0) """

    FF_STIRRUP_CAGES_INSTALLATION_SITE = 1097
    """ Installation site = building site (1 otherwise 0) """

    START_OF_SHORTENING = 1098
    """ Start of shortening """

    END_OF_SHORTENING = 1099
    """ End of shortening """

    NAME_NUMBER = 1100
    """ Name, number """

    OCCUPANCY_TYPE = 1101
    """ Occupancy type """

    HIERARCHIC__FUNCTION = 1102
    """ Function in hierarchy """

    PIPE_SECTION_TYPE = 1103
    """ Pipe section """

    WIDTH_DIAMETER = 1104
    """ Width, diameter """

    CLEAR_HEIGHT = 1105
    """ Clear height of rooms (finishing surfaces being subtracted) """

    START_HEIGHT = 1106
    """ Start height """

    END_HEIGHT = 1107
    """ End height """

    HEIGHT_DEFINITION = 1108
    """ Height definition """

    LOCATION = 1109
    """ Location """

    STATUS_CADASTRE = 1110
    """ Status """

    YEAR_OF_CONSTRUCTION = 1111
    """ Year of construction """

    HYDRAULIC_FUNCTION = 1112
    """ Hydraulic function """

    CONNECTION_TYPE = 1113
    """ Connection type """

    PROFILE_FIXTURES = 1114
    """ Profile fixtures """

    FOUNDATION_ENVELOPE = 1115
    """ Foundation, envelope """

    DRAINAGE_SYSTEM = 1116
    """ Drainage system """

    INCLINATION = 1117
    """ Inclination """

    LENGTHS = 1118
    """ Effective length """

    OWNERS = 1119
    """ Owner """

    LAST_MODIFICATION = 1120
    """ Last modification """

    HEIGHTS = 1122
    """ Height """

    TYPE_FUNCTION = 1123
    """ Type, function """

    DIMENSION1 = 1124
    """ Dimension 1 """

    DIMENSION2 = 1125
    """ Dimension 2 """

    BASE_HEIGHT = 1126
    """ Base level """

    FOUNDATION_HEIGHT = 1127
    """ Floor level """

    ACCESS_AID = 1128
    """ Access aid """

    ACCESSIBILITY = 1129
    """ Accessibility """

    NOMINAL_VOLUME = 1130
    """ Nominal volume """

    DIRECTION = 1131
    """ Effective direction """

    POSITION_IN_CONDUIT = 1132
    """ Position in conduit """

    POSITION = 1133
    """ Position """

    HEIGHT_DIFFERENCE = 1134
    """ Height difference, lift """

    OVERFLOW_HEIGHT = 1135
    """ Height, overflow """

    MANUFACTURER = 1136
    """ Manufacturer """

    CHARACTERISTICS = 1137
    """ Characteristics """

    INSTALLATION_DATE = 1138
    """ Installation date """

    LAST_CHECK = 1139
    """ Last check """

    INSULATION_ON_OUTSIDE = 1140
    """ Insulation on the outside """

    COATING_ON__INSIDE = 1141
    """ Coating on the inside """

    SHEAR_RESTRAINT = 1142
    """ Shearing protection """

    PLACING_MODE = 1143
    """ Placing mode """

    COVER = 1144
    """ Cover """

    OPERATING_PRESSURE = 1145
    """ Operating pressure """

    EXTENSION_TYPE = 1146
    """ Extension type """

    SWITCHING_STATE = 1147
    """ Switching state """

    SWITCHING_OPERATION = 1148
    """ Switching operation """

    FUNCTION_GENERAL = 1149
    """ Function, general """

    YEAR_OF_INSTALLATION = 1150
    """ Year of installation """

    DIMENSION = 1151
    """ Unit """

    OPERATOR = 1152
    """ Operator """

    CONCESSIONER = 1153
    """ Concessionaire """

    LIABILITY_FOR_MAINTENANCE = 1154
    """ Liability for maintenance """

    NODE_TYPE = 1155
    """ Node type of a tree structure (root, node, item) """

    OPERATING_PRESSURE_OF_SYSTEM = 1156
    """ Operating pressure of system """

    MAX_OPERATING_PRESSURE = 1157
    """ Maximum operating pressure """

    PRESSURE_ZONE = 1158
    """ Pressure zone """

    DOCUMENTS = 1159
    """ Documents """

    WATER_QUALITY = 1160
    """ Water quality """

    VOLUMETRIC_CAPACITY = 1162
    """ Volumetric capacity """

    PROCESS_WATER_RESERVES = 1163
    """ Process water reserves """

    WATER_RESERVES_FOR_FIREFIGHTING = 1164
    """ Water reserves for firefighting """

    NUMBER = 1165
    """ Number """

    NAMING = 1166
    """ Name """

    COMMENT = 1167
    """ Comment """

    FROM_MANHOLE = 1174
    """ From manhole """

    TO_MANHOLE = 1175
    """ To manhole """

    INNER_DIAMETER = 1176
    """ Inside diameter """

    OUTER_DIAMETER = 1177
    """ Outside diameter """

    HEIGHT_OF_MANHOLE = 1178
    """ Height of manhole """

    MATERIAL_OF_MANHOLE = 1179
    """ Material of manhole """

    SHAPE_OF_MANHOLE = 1180
    """ Shape of manhole """

    SIZE_OF_MANHOLE_COVER = 1181
    """ Size of manhole cover """

    MATERIAL_OF_MANHOLE_COVER = 1182
    """ Material of manhole cover """

    HOUSE_NUMBER = 1183
    """ House number """

    LOT_OF_LAND_NO_ = 1184
    """ Lot number """

    MANHOLE_COVER = 1185
    """ Manhole cover """

    STREET = 1186
    """ Street """

    SIZE_OF_MANHOLE = 1189
    """ Size of manhole """

    STATE_OF_MANHOLE_1 = 1190
    """ MS_1 (state 1 of manhole) """

    STATE_OF_MANHOLE_2 = 1191
    """ MS_2 (state 2 of manhole) """

    STATE_OF_MANHOLE_3 = 1192
    """ MS_3 (state 3 of manhole) """

    STATE_OF_MANHOLE_4 = 1193
    """ MS_4 (state 4 of manhole) """

    STATE_OF_MANHOLE_5 = 1194
    """ MS_5 (state 5 of manhole) """

    STATE_OF_MANHOLE_6 = 1195
    """ MS_6 (state 6 of manhole) """

    STATE_OF_MANHOLE_7 = 1196
    """ MS_7 (state 7 of manhole) """

    STATE_OF_MANHOLE_8 = 1197
    """ MS_8 (state 8 of manhole) """

    STATE_OF_MANHOLE_9 = 1198
    """ MS_9 (state 9 of manhole) """

    NETHERLANDS_X2 = 1200
    """ Netherlands: X2 """

    NETHERLANDS_Y2 = 1201
    """ Netherlands: Y2 """

    NETHERLANDS_BUIG_MIDDELL_ = 1202
    """ Netherlands: Buig middell. """

    NETHERLANDS_SPIRAAL_AANT_WIND_ = 1203
    """ Netherlands: Spiraal-aant.wind. """

    NETHERLANDS_SPIRAAL_SPOED = 1204
    """ Netherlands: Spiraal-spoed """

    NETHERLANDS_U = 1205
    """ Netherlands: U """

    NETHERLANDS_H1 = 1206
    """ Netherlands: H1 """

    NETHERLANDS_H2 = 1207
    """ Netherlands: H2 """

    TYPE_AMP_SIZE_FOR_BRITISH_STANDARD = 1208
    """ Reinforcement schedule based on British Standard: type and size """

    COMMENT_WITH_DEFAULT_VALUE = 1209
    """ Comment with default value """

    FILTER_BY_MESH = 1210
    """ Filter by mesh """

    NUMBER_OF_LONGITUDINAL_BARS = 1211
    """ Number of longitudinal bars in mesh """

    NUMBER_OF_CROSS_BARS = 1212
    """ Number of cross bars in mesh """

    MESH_TYPE = 1213
    """ Mesh type """

    TYPE_OF_LONGITUDINAL_BAR_DIAMETER = 1214
    """ Reinforcement schedule based on British Standard: type and longitudinal bar diameter """

    TYPE_OF_CROSS_BAR_DIAMETER = 1215
    """ Reinforcement schedule based on British Standard: type and cross bar diameter """

    SUMMARY_OF_REMARKS = 1216
    """ Comment, summary """

    LONGITUDE = 1217
    """ Project attribute: longitude """

    LATITUDE = 1218
    """ Project attribute: latitude """

    NET_VOLUME_OF_CONCRETE = 1219
    """ Net volume of concrete """

    FF_STIRRUP_CAGES_AVAILABILITY_STOCK_ITEMS = 1220
    """ FF stirrup cages, availability of stock items (1/0) """

    FF_STIRRUP_CAGES_AVAILABILITY_SPECIAL_REINFORCEMENT = 1221
    """ FF stirrup cages, availability of special reinforcement (1/0) """

    FF_STIRRUP_CAGES_SUPPLIER_EXTERNAL = 1222
    """ FF stirrup cages, external supplier (1/0) """

    FF_STIRRUP_CAGES_SUPPLIER_WORKS = 1223
    """ FF stirrup cages, supplied by factory (1/0) """

    FF_STIRRUP_CAGES_PRODUCER_EXTERNAL = 1224
    """ FF stirrup cages, external producer (1/0) """

    FF_STIRRUP_CAGES_PRODUCER_WORKS = 1225
    """ FF stirrup cages, produced by factory (1/0) """

    LAYER_ADJUSTMENT_TL = 1226
    """ Layer adjustment at top level [m] """

    LAYER_ADJUSTMENT_BL = 1227
    """ Layer adjustment at bottom level [m] """

    HEIGHT_WINDOW_SILL_OUTSIDE = 1228
    """ Height of outside window sill """

    HEIGHT_WINDOW_SILL_INSIDE = 1229
    """ Height of inside window sill """

    OFFSET_OPENING_BOTTOM = 1230
    """ Tolerance for calculating the lower dimensions of windows and doors """

    OFFSET_OPENING_TOP = 1231
    """ Tolerance for calculating the upper dimensions of windows and doors """

    OFFSET_OPENING_LEFT = 1232
    """ Tolerance for calculating the left dimensions of windows and doors """

    OFFSET_OPENING_RIGHT = 1233
    """ Tolerance for calculating the right dimensions of windows and doors """

    ASSOCIATION_WITH_GROUP = 1246
    """ Associated with fixture group """

    STONE_TYPE = 1247
    """ Tile type """

    DAMAGE_1_CHANNEL = 1250
    """ Damage 1 (conduit) """

    DAMAGE_2_CHANNEL = 1251
    """ Damage 2 (conduit) """

    DAMAGE_3_CHANNEL = 1252
    """ Damage 3 (conduit) """

    DAMAGE_4_CHANNEL = 1253
    """ Damage 4 (conduit) """

    DAMAGE_5_CHANNEL = 1254
    """ Damage 5 (conduit) """

    DAMAGE_6_CHANNEL = 1255
    """ Damage 6 (conduit) """

    DAMAGE_7_CHANNEL = 1256
    """ Damage 7 (conduit) """

    DAMAGE_8_CHANNEL = 1257
    """ Damage 8 (conduit) """

    DAMAGE_9_CHANNEL = 1258
    """ Damage 9 (conduit) """

    COMMENT_SB = 1259
    """ Comment (MD) """

    COMMENT_KZ = 1260
    """ Comment (CS) """

    COMMENT_KB = 1261
    """ Comment (CD) """

    COMMENT_SZ = 1262
    """ Comment (MS) """

    CODE_MANHOLE = 1263
    """ Code, manhole """

    CODE_CHANNEL = 1264
    """ Code, conduit """

    POSITION_1_CHANNEL = 1265
    """ Position 1 (conduit) """

    POSITION_2_CHANNEL = 1266
    """ Position 2 (conduit) """

    POSITION_3_CHANNEL = 1267
    """ Position 3 (conduit) """

    POSITION_4_CHANNEL = 1268
    """ Position 4 (conduit) """

    POSITION_5_CHANNEL = 1269
    """ Position 5 (conduit) """

    POSITION_6_CHANNEL = 1270
    """ Position 6 (conduit) """

    POSITION_7_CHANNEL = 1271
    """ Position 7 (conduit) """

    POSITION_8_CHANNEL = 1272
    """ Position 8 (conduit) """

    POSITION_9_CHANNEL = 1273
    """ Position 9 (conduit) """

    DEDUCTION_OPENING_BOTTOM = 1274
    """ Constant offset at the bottom for calculating the clear width """

    CONDUIT_MATERIAL = 1275
    """ Conduit material """

    CONDUIT_DIMENSION = 1276
    """ Conduit dimension """

    COMMENT__WL = 1277
    """ Comment (TC) """

    L_DIM__DN = 1278
    """ L Dim (DN) """

    L_DIM__DI = 1279
    """ L Dim (di) """

    L_DIM__DE = 1280
    """ L Dim (de) """

    DATE_OF_REVISION = 1281
    """ Date of revision """

    TYPE_OF_HYDRANT = 1282
    """ Type of hydrant """

    OUTFLOW_OF_HYDRANTS = 1283
    """ Outflow of hydrants """

    HYDRANT_NO_ = 1284
    """ Hydrant number """

    SLIDE_NO_ = 1285
    """ Slide number """

    TYPE_OF_SLIDE = 1286
    """ Type of slide """

    LOCATION_OF_DAMAGE = 1287
    """ Location of damage """

    KIND_OF_DAMAGE = 1288
    """ Kind of damage """

    DAMAGE_TO_OBJECT = 1289
    """ Damage to object """

    REPAIR_COSTS = 1290
    """ Repair costs """

    SEWER_GRID_ELEMENT_REF = 1291
    """ Reference element of sewer network """

    OUTFLOW_COEFFICIENT = 1292
    """ Outflow coefficient """

    MATERIAL_CODE = 1293
    """ Material code """

    OCCUPANCY_TYPE_ID = 1294
    """ Occupancy type ID """

    DELTA_VALUE_FOR_INITIAL_HEIGHT = 1295
    """ Delta value for initial height """

    DELTA_VALUE_FOR_FINAL_HEIGHT = 1296
    """ Delta value for final height """

    MANHOLE_REF = 1297
    """ Reference manhole """

    CONDUIT_REF = 1298
    """ Reference conduit """

    CALCULATION_OF_LENGTH = 1299
    """ Calculation of length """

    INLET_1 = 1300
    """ Inlet 1 """

    INLET_2 = 1301
    """ Inlet 2 """

    INLET_3 = 1302
    """ Inlet 3 """

    SHAFT_OUTLET = 1303
    """ Outlet """

    STOREY = 1304
    """ Story """

    SITE_AREA_RATIO = 1305
    """ Site area ratio """

    LEVEL_OF_SENSITIVITY = 1306
    """ Level of sensitivity """

    SYMBOL_ORI = 1307
    """ Symbol orientation """

    SPECIAL_BUILDING_REF = 1308
    """ Special building reference """

    TEXT = 1310
    """ Text (for export) """

    TEXT_POS = 1311
    """ Text position """

    STAGE = 1312

    TEXT_HALI = 1313
    """ Text, horizontally aligned """

    TEXT_VALI = 1314
    """ Text, vertically aligned """

    INLET = 1315
    """ Inlet """

    OUTLET = 1316
    """ Outlet """

    OBJ_ID = 1319
    """ Internal Allplan object ID(Guid) """

    SEALING_FACTOR = 1320
    """ Sealing factor """

    POPULATION_DENSITY = 1321
    """ Population density """

    MD_DATA_ADMINISTRATOR = 1322
    """ Data administrator """

    SUPERCLASS = 1323
    """ Superclass """

    INNER_PROTECTION = 1324
    """ Internal treatment """

    FRICTION_COEFFICIENT = 1325
    """ Friction coefficient """

    WALL_ROUGHNESS = 1326
    """ Wall roughness """

    SEEPAGE = 1327
    """ Seepage """

    CATALOG_REFERENCE = 1332
    """ Catalog reference """

    MATCHCODE = 1333
    """ Fixtures: match code """

    ASSOCIATED_PRECAST_ELEMENT = 1334
    """ Fixtures: associated with precast element """

    ASSOCIATED_PRECAST_WALL_ELEMENT = 1335
    """ Fixtures: associated with precast wall element """

    ASSOCIATED_PRECAST_SLAB_ELEMENT = 1336
    """ Fixtures: associated with precast slab element """

    ASSOCIATED_STRUCTURAL_PRECAST_ELEMENT = 1337
    """ Fixtures: associated with structural precast element """

    ASSOCIATED_ARCHITECTURAL_WALL = 1338
    """ Fixtures: associated with architectural wall """

    ASSOCIATED_ARCHITECTURAL_SLAB = 1339
    """ Fixtures: associated with architectural slab """

    INTERFACE_TYPE = 1340

    STIRRUP_LENGTH = 1341

    LONGIT__BAR_LENGTH = 1342

    STIRRUP_DIAMETER = 1343

    LONGIT__BAR_DIAMETER = 1344

    OFFSET_AT_START = 1345

    STIRRUP_NUMBER = 1346

    STIRRUP_SPACING = 1347

    DOMED_ROOF_LIGHT_CURB_HEIGHT = 1348
    """ Domed roof-light, curb height """

    DOMED_ROOF_LIGHT_DOME_HEIGHT = 1349
    """ Domed roof-light, rise """

    CATALOG_LIST_TEXT = 1350
    """ List text from fixture catalog for precast elements """

    UNSPSC_NAME = 1352
    """ Categorization - UNSPSC Name """

    UNSPSC_CODE = 1353
    """ Categorization - UNSPSC Code """

    UNICLASS_1_4_CODE = 1354
    """ Categorization - Uniclass 1.4 Code """

    TYPE_OF_MATERIAL = 1355
    """ Material type (concrete...0, insulation...1, in-situ concrete...2, bricks/tiles...3) """

    UNICLASS_1_4_DESCRIPTION = 1356
    """ Categorization - Uniclass 1.4 Beschreibung """

    UNICLASS_2_0_CODE = 1357
    """ Categorization - Uniclass 2.0 Code """

    UNICLASS_2_0_DESCRIPTION = 1358
    """ Categorization - Uniclass 2.0 Beschreibung """

    NBS_REFERENCE_CODE = 1359
    """ Categorization - NBS Reference Code """

    MESH_STEEL_WEIGHT = 1365
    """ Reinforcing mesh weight """

    BAR_STEEL_WEIGHT = 1366
    """ Reinforcing bar weight """

    LATTICE_GIRDER_STEEL_WEIGHT = 1367
    """ Lattice girder weight """

    DEDUCTION_OPENING_LEFT = 1368
    """ Constant offset on the left for calculating the clear width """

    DEDUCTION_OPENING_RIGHT = 1369
    """ Constant offset on the right for calculating the clear width """

    DEDUCTION_OPENING_TOP = 1370
    """ Constant offset at the top for calculating the clear width """

    COMBUSTIBLE = 1371
    """ BuildingSmart: Combustible """

    SURFACE_SPREAD_OF_FLAME = 1372
    """ Behavior under fire """

    ACOUSTIC_RATING = 1373
    """ Sound transmission class """

    SPAN = 1374
    """ Span """

    BARRIER_FREE = 1375
    """ Handicapped accessible """

    FIRE_EXIT_STAIR = 1376
    """ Means of egress """

    REQUIRED_HEADROOM = 1377
    """ Ifc: RequiredHeadroom """

    REQUIRED_SLOPE = 1378
    """ RequiredSlope """

    SMOKE_STOP = 1379
    """ IFC: SmokeStop """

    SELF_CLOSING = 1380
    """ Self-closing """

    FIRE_EXIT = 1381
    """ Emergency exit """

    MODEL_NUMBER = 1382
    """ IFC: ModelReference """

    MODEL_LABEL = 1383
    """ IFC: ModelLabel """

    ARCHITECT_MOBILE_NUMBER = 1384
    """ Architect, mobile number """

    ARCHITECT_HOMEPAGE = 1385
    """ Web address of architect """

    CLIENT_HOMEPAGE = 1386
    """ Web address of client """

    BUILDING_CONTRACTOR_HOMEPAGE = 1387
    """ Web address of a building contractor """

    CONSTRUCTION_PROJECT_HOMEPAGE = 1388
    """ Web address of construction project """

    CHECKING_STRUCTURAL_ENGINEER_HOMEPAGE = 1389
    """ Web address of structural inspection engineer """

    STRUCTURAL_ENGINEER__HOMEPAGE = 1390
    """ Web address of structural engineer """

    PLOT_AREA_WITH_BUILDING = 1391

    SECURITY_RATING = 1392

    PRODUCTION_YEAR = 1393

    FINISH = 1394

    CLASSIFICATION_KEY = 1395

    COMPARTMENTATION = 1396
    """ BuildingSmart: Compartmentation """

    PROJECTED_AREA = 1397

    FIRE_RISK_FACTOR = 1398

    SPRINKLER_PROTECTION = 1399

    ARTIFICIAL_LIGHTING = 1400

    SPACE_HUMIDITY = 1401

    NATURAL_VENTILATION = 1402

    AIR_CONDITIONED = 1403

    SPACE_TEMPERATURE_MAX = 1404

    SPACE_TEMPERATURE_MIN = 1405

    HAS_NON_SKID_SURFACE = 1406
    """ Adjustment to BuildingSmart: HasNonSkidSurface """

    MARK_NUMBERS_OF_MESHESBARSFIXTURES_IN_ELEMENT_PLAN = 1412
    """ Mark numbers of meshes/bars/fixtures in element plan """

    SIDE_OF_PRECAST_ELEMENT_LAYER = 1413
    """ Side of precast element layer """

    TYPE_OF_REINFORCEMENT = 1415
    """ Filter for reinforcement type (bar type, mesh type, girder type) """

    STANDARD_FORMWORK_ELEMENT_BOTTOM_STEP_NAME = 1416
    """ Standard formwork element, bottom step, name """

    STANDARD_FORMWORK_ELEMENT_NORMAL_AREA_NAME = 1417
    """ Standard formwork element, normal area, name """

    STANDARD_FORMWORK_ELEMENT_TOP_STEP_NAME = 1418
    """ Standard formwork element, top step, name """

    STANDARD_FORMWORK_ELEMENT_BOTTOM_STEP_LENGTH = 1419
    """ Standard formwork element, bottom step, length """

    STANDARD_FORMWORK_ELEMENT_NORMAL_AREA_LENGTH = 1420
    """ Standard formwork element, normal area, length """

    STANDARD_FORMWORK_ELEMENT_TOP_STEP_LENGTH = 1421
    """ Standard formwork element, top step, length """

    PROFILE_NAME = 1426

    PBB_REQUIREMENTS_1 = 1427

    PBB_REQUIREMENTS_2 = 1428

    PBB_REQUIREMENTS_3 = 1429

    PBB_REQUIREMENTS_4 = 1430

    PBB_REQUIREMENTS_5 = 1431

    BENDING_DIMENSIONS_ISO_3766_A_E = 1437
    """ Bending dimensions (a """

    BAR_SHAPE_CODE_ISO_3766 = 1438
    """ Bar shape key ISO 3766 """

    WEIGHTM = 1439
    """ Steel construction attribute describing the weight of a steel section that is one meter long """

    SHELL_SURFACEM = 1440
    """ Steel construction attribute describing the surface of a steel section that is one meter long """

    PURPOSE = 1441
    """ IFC Purpose: Indication of the purpose for that opening, e.g. "ventilation" acc. to BuildingSmart """

    EXTEND_TO_STRUCTURE = 1442
    """ IFC ExtendToStructure acc. to BuildingSmart """

    FORMWORK_TYPE = 1443
    """ Formwork types 1 to 4 """

    IFC_PREDEFINED_TYPE = 1444
    """ IFC object subtype """

    GLAZING_AREA_FRACTION = 1445
    """ IFC GlazingAreaFraction acc. to BuildingSmart """

    CROSS_SECTIONAL_AREA = 1446
    """ Cross-sectional area according to steel construction """

    CHARACTERISTIC_VALUE_OF_DEAD_LOAD = 1447
    """ Characteristic value of dead load according to steel construction """

    DESCRIPTION = 1448
    """ Description for Ifc mapping """

    NAME_OF_CONNECTION = 1450
    """ Name of connection """

    NUMBER_OF_CONNECTIONS = 1451
    """ Number of connections """

    SECONDARY_REINFORCEMENT_AT_CONNECTION = 1452
    """ Analyzes secondary reinforcement """

    WEIGHT_OF_CONNECTION = 1453
    """ Analyzes the weight of the connection """

    WALL_THICKNESS_AT_CONNECTION = 1454
    """ Analyzes the wall thickness of the connection """

    MRK_NO_OF_ELEMENTS = 1455
    """ Mark number of cage elements of the connection """

    DETAIL_DRAWING_FILE_NUMBER = 1458
    """ Drawing file number of associated detail precast element """

    MODEL_DRAWING_FILE_NUMBERS = 1459
    """ Drawing file numbers of associated model precast elements """

    MRK_NO_WITH_PREFIX_FOR_FIXTURES = 1460
    """ Mark number with prefix of fixtures """

    LATTICE_GIRDER_NAME = 1461
    """ Name of lattice girder type """

    LATTICE_GIRDER_TOTAL_WEIGHT = 1462
    """ Total weight of lattice girders """

    LATTICE_GIRDER_WEIGHT = 1463
    """ Weight of lattice girder """

    ADDITIONAL_ID = 1464
    """ Additional ID of precast element """

    NUMBER_OF_PAGES = 1465
    """ Total number of pages in element plan """

    ADDITIONAL_IDS_SAME_MARK_NUMBER = 1466
    """ Additional IDs of precast element group (same mark number) """

    INSULATING_STRIP_VOLUME = 1467
    """ Volume of insulating strip """

    STEEL_GRADE_OF_MESHES_BARS_IN_PRECAST_ELEMENT = 1468
    """ Steel grade of meshes, bars in precast element """

    MODEL_DRAWING_FILE_NAME = 1469
    """ Drawing file name of model drawing file name """

    ASSEMBLY_GROUP_NAME = 1470
    """ Name of associated assembly """

    NUMBER_OF_BAR_SPACING = 1471
    """ Number of bar spacing in placement """

    TOTAL_BAR_SPACING = 1472
    """ Total bar spacing in placement """

    NUMBER_OF_ELEMENTS_IN_DIMENSION_LINE_OF_ELEMENT_PLAN = 1473
    """ Number of elements in dimension line of element plan """

    INVOICE_ITEM_NAME = 1477
    """ Text of order item """

    INVOICE_ITEM_NUMBER = 1478
    """ Number within confirmation of order """

    INVOICE_ITEM_ID = 1479
    """ ID within confirmation of order """

    PAGE_NAME = 1480
    """ Page name of element plan page """

    LEAF_1__FORMWORK_BOTTOM = 1481
    """ Leaf 1 / formwork bottom """

    OMNI_CLASS_NUMBER = 1482
    """ no matter what """

    OMNI_CLASS_TITLE = 1483
    """ no matter what """

    UNICLASS_2015_CODE = 1484
    """ Categorization - till 2017: Uniclass-Number """

    UNICLASS_2015_DESCRIPTION = 1485
    """ Categorization - Uniclass 2015 Description """

    LAND_REGISTER___DISTRICT = 1486
    """ Land register - district """

    LAND_REGISTER___SUBDISTRICT = 1487
    """ Land register - subdistrict """

    LAND_REGISTER____SHEET_NUMBER = 1488
    """ Land register -  sheet number """

    LAND_REGISTER___PARCEL_NUMBER = 1489
    """ Land register - parcel number """

    STANDARD_ROOM_ASSIGNMENT = 1500
    """ Standard room assignment of Smartparts """

    FIGURE01 = 1830
    """ ALLFA: figure 01 """

    FIGURE02 = 1831
    """ ALLFA: figure 02 """

    FIGURE03 = 1832
    """ ALLFA: figure 03 """

    FIGURE04 = 1833
    """ ALLFA: figure 04 """

    FIGURE05 = 1834
    """ ALLFA: figure 05 """

    FIGURE06 = 1835
    """ ALLFA: figure 06 """

    FIGURE07 = 1836
    """ ALLFA: figure 07 """

    FIGURE08 = 1837
    """ ALLFA: figure 08 """

    FIGURE09 = 1838
    """ ALLFA: figure 09 """

    FIGURE10 = 1839
    """ ALLFA: figure 10 """

    NUMBER01 = 1840
    """ ALLFA: number 01 """

    NUMBER02 = 1841
    """ ALLFA: number 02 """

    NUMBER03 = 1842
    """ ALLFA: number 03 """

    NUMBER04 = 1843
    """ ALLFA: number 04 """

    NUMBER05 = 1844
    """ ALLFA: number 05 """

    DATE01 = 1845
    """ ALLFA: date 01 """

    DATE02 = 1846
    """ ALLFA: date 02 """

    DATE03 = 1847
    """ ALLFA: date 03 """

    DATE04 = 1848
    """ ALLFA: date 04 """

    DATE05 = 1849
    """ ALLFA: date 05 """

    SCIA_LENGTH = 1850
    """ SCIA length """

    SCIA_SURFACE = 1851
    """ SCIA surface """

    SCIA_VOLUME = 1852
    """ SCIA volume """

    SCIA_WEIGHT = 1853
    """ SCIA weight """

    SCIA_VERSION = 1854
    """ SCIA version """

    SCIA_TYPE = 1855
    """ SCIA type """

    TRUCK_NUMBER = 1857
    """ Truck number """

    MIRROR_FIRST_HOLE = 1858
    """ Fixtures, steel section - mirror first hole in section """

    SECTION_ORIENTATION = 1859
    """ Fixtures, steel section - section orientation (beam) """

    DOUBLE_SECTION = 1860
    """ Fixtures, steel section - double section """

    MOVE_HOLE = 1861
    """ Fixtures, steel section - dx hole in steel section """

    SECTION_TYPE = 1862
    """ Fixtures, steel section - steel section type (reference to catalog) """

    CONSTRUCTION_METHOD = 1864
    """ IFC ConstructionMethod, Excution (In-situ, Precast) """

    PRODUCT_DATA_LINK = 1865
    """ Product data link for BIMobject cooperation in 2017-1-1 """

    THICKNESS_OF_VISIBLE_LEAF = 1866
    """ Thickness of visible leaf """

    THICKNESS_OF_INVISIBLE_LEAF = 1867
    """ Thickness of invisible leaf """

    HEIGHT_OF_VISIBLE_LEAF = 1868
    """ Height of visible leaf """

    HEIGHT_OF_INVISIBLE_LEAF = 1869
    """ Height of invisible leaf """

    WIDTH_OF_VISIBLE_LEAF = 1870
    """ Width of visible leaf """

    WIDTH_OF_INVISIBLE_LEAF = 1871
    """ Width of invisible leaf """

    STANDARD_GIRDER_TYPE = 1872
    """ Standard type of lattice girder """

    MINIMUM_OFFSET_TO_EDGE = 1873
    """ Minimum offset to edge """

    ADDITIONAL_TEXT_FOR_KEY_PLAN = 1875
    """ Additional text for key plan """

    CONCR__TOPPING = 1876
    """ Concrete topping """

    PRECAST_ID = 1877
    """ Unique ID for precast elements """

    C_I_NUT_TYPE = 1878
    """ Assembly - type of cast-in nut """

    REQUIRED_ASX_AT_TOPVISIBLE = 1879
    """ Required longitudinal as-value at top/visible """

    REQUIRED_ASX_AT_BOTTOMINVISIBLE = 1880
    """ Required longitudinal as-value at bottom/invisible """

    EXISTING_ASX_AT_TOPVISIBLE = 1881
    """ Existing longitudinal as-value at top/visible """

    EXISTING_ASX_AT_BOTTOMINVISIBLE = 1882
    """ Existing longitudinal as-value at bottom/invisible """

    REQUIRED_ASY_AT_TOPVISIBLE = 1883
    """ Required transverse as-value at top/visible """

    REQUIRED_ASY_AT_BOTTOMINVISIBLE = 1884
    """ Required transverse as-value at bottom/invisible """

    EXISTING_ASY_AT_TOPVISIBLE = 1885
    """ Existing transverse as-value at top/visible """

    EXISTING_ASY_AT_BOTTOMINVISIBLE = 1886
    """ Existing transverse as-value at bottom/invisible """

    DATE_ON_WHICH_DATA_WAS_TRANSFERRED_TO_PRODUCTION = 1887
    """ Date on which data was transferred to production """

    STATUS_NAME = 1889
    """ Name of precast element status """

    STATUS_DESCRIPTION = 1890
    """ Description of precast element status """

    STATUS_SEQUENCE = 1891
    """ Sequence of precast element status """

    SLAB_THICKNESS = 1892
    """ Slab thickness """

    COMPONENT_NAME = 1893
    """ Name of precast element """

    INVOICE_TEXT = 1894
    """ Invoice item of precast element """

    CUSTOM_ATTRIBUTE_06 = 1895
    """ Precast elements: custom attribute 06 --&gt; included for compatibility reasons only! Use 1947! """

    CUSTOM_ATTRIBUTE_07 = 1896
    """ Precast elements: custom attribute 07 --&gt; included for compatibility reasons only! Use 1947! """

    CUSTOM_ATTRIBUTE_08 = 1897
    """ Precast elements: custom attribute 08 --&gt; included for compatibility reasons only! Use 1947! """

    CUSTOM_ATTRIBUTE_09 = 1898
    """ Precast elements: custom attribute 09 --&gt; included for compatibility reasons only! Use 1947! """

    CUSTOM_ATTRIBUTE_10 = 1899
    """ Precast elements: custom attribute 10 --&gt; included for compatibility reasons only! Use 1947! """

    CUSTOM_ATTRIBUTE_11 = 1900
    """ Precast elements: custom attribute 11 --&gt; included for compatibility reasons only! Use 1947! """

    CUSTOM_ATTRIBUTE_12 = 1901
    """ Custom attribute 12 -&gt; only necessary due to compatibility! Use 1947 """

    CUSTOM_ATTRIBUTE_13 = 1902
    """ Custom attribute 13 -&gt; only necessary due to compatibility! Use 1947 """

    CUSTOM_ATTRIBUTE_14 = 1903
    """ Custom attribute 14 -&gt; only necessary due to compatibility! Use 1947 """

    CUSTOM_ATTRIBUTE_15 = 1904
    """ Custom attribute 15 -&gt; only necessary due to compatibility! Use 1947 """

    CONCRETE_STRENGTH_GRADE = 1905
    """ Concrete strength grade """

    VALUE_FOR_FOUNDATION_MODULUS = 1906
    """ FEA PLT: foundation modulus """

    INTERNAL_DIM__1 = 1907
    """ FEA PLT: internal dimension 1 """

    INTERNAL_DIM__2 = 1908
    """ FEA PLT: internal dimension 2 """

    EFFECTIVE_WIDTH = 1909
    """ FEA PLT: effective slab width """

    REINFORCEMENT_LAYER = 1910
    """ FEA PLT: layer """

    MESH = 1911
    """ FEA PLT: mesh """

    AS_1 = 1912
    """ FEA PLT: as 1 """

    AS_2 = 1913
    """ FEA PLT: as 2 """

    FZ = 1914
    """ FEA PLT: Fz """

    MX = 1915
    """ FEA PLT: Mx """

    MY = 1916
    """ FEA PLT: My """

    FEM_PLT_QZ = 1917
    """ FEA PLT: qz [kN/m] """

    FEM_PLT_QZ_2 = 1918
    """ FEA PLT: qz 2 """

    M = 1919
    """ FEA PLT: m """

    M_2 = 1920
    """ FEA PLT: m 2 """

    FEM_PLT_QZ_3 = 1921
    """ FEA PLT: qz [kN/m2] """

    TEMPERATURE_AT_TOP = 1922
    """ FEA PLT: temperature at top """

    TEMPERATURE_AT_BOTTOM = 1923
    """ FEA PLT: temperature at bottom """

    MATERIAL_TYPE = 1924
    """ FEA PLT: material type """

    FEM_PLT_WIDTH = 1925
    """ FEA PLT: width """

    FEM_PLT_DIAMETER = 1926
    """ FEA PLT: diameter """

    FEM_PLT_TYPE = 1927
    """ FEA PLT: type """

    FEM_PLT_ANGLE = 1928
    """ FEA PLT: angle """

    PRECAST_IDS_SAME_MARK_NO_ = 1929
    """ Precast elements: precast IDs (same mark number) """

    SPAN_DIRECTION = 1930
    """ Precast elements: span direction """

    NUMBER_OF_SAME_FOUNDATIONS = 1931
    """ Number of same foundations """

    CONSECUTIVE_NUMBER = 1932
    """ Consecutive number """

    BOTTOM_EDGE_OF_FOUNDATION = 1933
    """ Bottom level of foundation """

    FOUNDATION_DIMENSIONS_M = 1934
    """ Foundation dimensions [m] """

    BOTTOM_EDGE_OF_COLUMN_____FOUNDATION = 1935
    """ Bottom level of column ... foundation """

    SYMBOL = 1936
    """ Symbol """

    PILE_LOAD_K_N = 1937
    """ Pile load [kN] """

    PILE_DIAMETER_M = 1938
    """ Pile diameter [m] """

    TOP_OF_PILE_M = 1939
    """ Top level of pile [m] """

    NUMBER_OF_SAME_PILES = 1940
    """ Number of same piles """

    NAME_OF_FILLING_OBJECT = 1941
    """ Precast elements: name of filling object """

    NUMBER_OF_FILLING_OBJECTS = 1942
    """ Precast elements: number of filling objects """

    MRK__NO__OF_MESHESBARS_IN_ELEMENT_PLAN = 1943
    """ Mark number of meshes, bars in element plan """

    NAME_OF_PROFILE = 1944
    """ Sleeve foundation - support foot - name of profiling """

    HEIGHT_OF_PROFILE = 1945
    """ Sleeve foundation - support foot - height of profiling """

    NUMBER_OF_MESHESBARSFIXTURES_IN_ELEMENT_PLAN = 1946
    """ Number of meshes, bars, fixtures in element plan """

    CUSTOM_ATTRIBUTE = 1947
    """ Precast elements: custom attributes (including index 1-n) """

    WEIGHT_OF_MESHESBARS_IN_ELEMENT_PLAN = 1948
    """ Weight of meshes, bars in element plan """

    LD_TYPE = 1949

    MARK_NUMBER_LIST = 1950

    FILLING_OBJECT_DIAMETER = 1951

    BRICK_NAME = 1952

    BRICK_LENGTH = 1953

    GRID_DIMENSION = 1954

    LENGTH_OF_BARS_IN_ELEMENT_PLAN = 1955
    """ Length of bars in element plan [m] """

    IN_SITU_CONCRETE_GRADE = 1956
    """ Concrete grade of in-situ concrete layer """

    ROLL = 1957
    """ Roll(IfcPlaneAngleMeasure) """

    PITCH_ANGLE = 1958
    """ PitchAngle(IfcPlaneAngleMeasure) """

    GROSS_PLANNED_AREA = 1959
    """ GrossPlannedArea(IfcAreaMeasure) """

    NET_PLANNED_AREA = 1960
    """ NetPlannedArea(IfcAreaMeasure) """

    PUBLICLY_ACCESSIBLE = 1961
    """ PubliclyAccessible(IfcBoolean) """

    PROTECTED_OPENING = 1962
    """ ProtectedOpening(IfcBoolean) """

    INFILTRATION = 1963
    """ Infiltration(IfcVolumetricFlowRateMeasure) """

    HAS_DRIVE = 1964
    """ HasDrive(IfcBoolean) """

    WATER_TIGHTNESS_RATING = 1965
    """ WaterTightnessRating(IfcLabel) """

    MECHANICAL_LOAD_RATING = 1966
    """ MechanicalLoadRating(IfcLabel) """

    WIND_LOAD_RATING = 1967
    """ WindLoadRating(IfcLabel) """

    WALKING_LINE_OFFSET = 1968
    """ WalkingLineOffset(IfcPositiveLenghtMeasure) """

    TREAD_LENGTH_AT_OFFSET = 1969
    """ TreadLengthAtOffset(IfcPositiveLenghtMeasure) """

    FRAGILITY_RATING = 1970
    """ FragilityRating(IfcLabel) """

    MINIMUM_WAIST_THICKNESS = 1971
    """ WaistThickness(IfcPositiveLenghtMeasure) """

    NUMBER_OF_DRAFTS = 1972
    """ NumberOfDrafts(IfcCountMeasure) """

    NOSING_LENGTH = 1973
    """ NosingLength(IfcLengthMeasure) """

    TREAD_LENGTH_AT_INNER_SIDE = 1974
    """ TreadLengthAtInnerSide(IfcPositiveLenghtMeasure) """

    HAS_SILL_EXTERNAL = 1975
    """ HasSillExternal(IfcBoolean) """

    HAS_SILL_INTERNAL = 1976
    """ HasSillInternal(IfcBoolean) """

    NUMBER_OF_TREADS = 1977
    """ NumberOfTreads(IfcCountMeasure) """

    LENGTHINCH_PER_M = 1980
    """ Length [inch] (per meter) - string """

    LAYER_NUMBER_OF_PRECAST_ELEMENT = 1981
    """ Layer number of precast element """

    MWS_REINFORCEMENT_GROUP_FILTER = 1982
    """ MWS reinforcement group filter (is it a group? 0/1) """

    STACK_NAME = 1983
    """ Stack name: text for stack name """

    ARCHITECT_EMAIL = 1984
    """ Architect, email """

    CLIENT_FAX_NUMBER = 1985
    """ Client, fax number """

    CLIENT_TELEPHONE_NUMBER = 1986
    """ Client, telephone number """

    CLIENT_MOBILE_NUMBER = 1987
    """ Client, mobile number """

    CLIENT_EMAIL = 1988
    """ Client, email """

    BUILDING_CONTRACTOR = 1989
    """ Building contractor """

    BUILDING_CONTRACTOR_FAX_NUMBER = 1990
    """ Building contractor, fax number """

    BUILDING_CONTRACTOR_TELEPHONE_NUMBER = 1991
    """ Building contractor, telephone number """

    BUILDING_CONTRACTOR_MOBILE_NUMBER = 1992
    """ Building contractor, mobile number """

    BUILDING_CONTRACTOR_EMAIL = 1993
    """ Building contractor, email """

    CONSTRUCTION_PROJECT_MOBILE_NUMBER = 1994
    """ Construction project, mobile number """

    CONSTRUCTION_PROJECT_EMAIL = 1995
    """ Construction project, email """

    CHECKING_STRUCTURAL_ENGINEER_MOBILE_NUMBER = 1996
    """ Structural inspection engineer, mobile number """

    CHECKING_STRUCTURAL_ENGINEER_EMAIL = 1997
    """ Structural inspection engineer, email """

    STRUCTURAL_ENGINEER_MOBILE_NUMBER = 1998
    """ Structural engineer, mobile number """

    STRUCTURAL_ENGINEER_EMAIL = 1999
    """ Structural engineer, email """

    DO_NOT_SPLIT_IN_IFC = 18001
    """ Prevents the splitting of multilayer elements """

    INNER_WEB_HEIGHT = 18002

    MINIMUM_BEARING_SEAT_DEPTH = 18003

    UNIT_WARPING_AT_FLANGE_ROOT_WM1 = 18004

    RADIUS_R3 = 18005

    INTERNAL_BOLT_DISTANCE = 18006

    FLANGE_THICKNESS_BOTTOM = 18007

    INNER_RADIUS__R_ = 18008

    WIDTH__B_ = 18009

    WEB_THICKNESS__TD_ = 18010

    THICKNESS__S_ = 18011

    RADIUS_R1 = 18012

    UNIT_WARPING_AT_FLANGE_TOE = 18013

    OUTER_RADIUS = 18014

    FLANGE_WIDTH_BOTTOM = 18015

    DEPTH_OF_WEB = 18016

    BOLT_DISTANCE_W3 = 18017

    FLANGE_SLOPE__A_ = 18018

    PLUSLIP_ANGLE__A2_ = 18019

    INTERMEDIATE_BOTTOM_HEIGHT_F2 = 18020

    WEB_THICKNESS__S_ = 18021

    PLUSLIP = 18022

    INNER_LENGTH = 18023

    PLUSLIP_ANGLE__A_ = 18024

    WIDTH_TOP = 18025

    INTERMEDIATE_TOP_HEIGHT__H2_ = 18026

    LIP_TOP = 18027

    LIP = 18028

    WEB_DEPRESSION = 18029

    FLANGE_THICKNESS__T_ = 18030

    FLANGE_SLOPE__A1_ = 18031

    THICKNESS__T_ = 18032

    RADIUS_R2 = 18033

    INTERMEDIATE_WIDTH__B2_ = 18034

    FLANGE_WIDTH_TOP = 18035

    LIP_ANGLE = 18036

    INTERMEDIATE_WIDTH__B3_ = 18037

    THICKNESS__W_ = 18038

    BOLT_DISTANCE_W1 = 18039

    FLANGE_ANGLE = 18040

    FLANGE_THICKNESS__TB_ = 18041

    INNER_RADIUS__R1 = 18042

    UNIT_WARPING_AT_FLANGE_TOE_WM2 = 18043

    RADIUS_AT_FLANGE_TOE = 18044

    HEIGHT__H_ = 18045

    BOLT_DISTANCE_W2 = 18046

    INTERMEDIATE_TOP_HEIGHT__H3_ = 18047

    DEPTH = 18049

    WIDTH_BOTTOM = 18050

    WEB_HEIGHT_NEAR_FLANGE = 18051

    WEB_SLOPE = 18052

    TOTAL_WIDTH = 18053

    RADIUS_R5 = 18054

    RADIUS_AT_WEB_ROOT = 18055

    FLANGE_THICKNESS_TOP = 18056

    DIAMETER__D_ = 18057

    INTERMEDIATE_BOTTOM_HEIGHT_F3 = 18058

    LIP_BOTTOM = 18059

    FLANGE_WIDTH = 18060

    WEAR = 18061

    RADIUS_R4 = 18062

    RADIUS_AT_FLANGE_ROOT = 18063

    INTERMEDIATE_BOTTOM_HEIGHT_F1 = 18064

    NUMBER_OF_PRECAST_ELEMENTS = 18065
    """ Returns the number of precast elements including the piece factor """

    X_DIMENSION = 18066

    Y_DIMENSION = 18067

    Z_DIMENSION = 18068

    STYLE_NAME = 18071
    """ Name of selected architectural style """

    BENDING_DIMENSIONS_ACI_A_R = 18072

    BENDING_SHAPE_KEY_ACI = 18073

    FLAMMABILITY_RATING = 18074
    """ IFC flammability rating """

    ENTRANCE_LEVEL = 18075
    """ IFC entrance level """

    DURABILITY_RATING = 18076
    """ Durability rating """

    HYGROTHERMAL_RATING = 18077
    """ Hygrothermal rating """

    ABOVE_GROUND = 18078
    """ IFC above ground """

    AUTOMATIC_SPRINKLER_PROTECTION = 18079
    """ IFC sprinkler protection, automatic """

    PREAST_ELEMENT_ROTATION_DIRECTION = 18081

    LOAD_BEARING_CAPACITY = 18082
    """ IFC load-bearing capacity """

    BENDING_DIMENSIONS_ACI_A = 18091

    BENDING_DIMENSIONS_ACI_B = 18092

    BENDING_DIMENSIONS_ACI_C = 18093

    BENDING_DIMENSIONS_ACI_D = 18094

    BENDING_DIMENSIONS_ACI_E = 18095

    BENDING_DIMENSIONS_ACI_F = 18096

    BENDING_DIMENSIONS_ACI_G = 18097

    BENDING_DIMENSIONS_ACI_H = 18098

    BENDING_DIMENSIONS_ACI_J = 18099

    BENDING_DIMENSIONS_ACI_K = 18100

    BENDING_DIMENSIONS_ACI_O = 18101

    BENDING_DIMENSIONS_ACI_R = 18102

    BIM_OBJECT_ID = 18103
    """ For objects downloaded from BimObject """

    SHAPE = 18104

    COATING = 18105

    NAME_OF_STRUCTURAL_CROSS_SECTION = 18106

    BELOW_TERRAIN = 18107
    """ Below terrain -&gt; for Switzerland """

    LOAD = 18108
    """ Column load or point load """

    CONCRETE_OVERLAP = 18109
    """ Concrete overlap """

    IMPACT_LOAD = 18110
    """ Impact load """

    EXPOSED_CONCRETE_CLASS = 18111
    """ Exposed concrete class """

    SURFACE_NPK = 18112
    """ Surface NPK for Switzerland """

    SPREADER_HEIGHT = 18113
    """ Spreader height for Switzerland """

    OPERATION = 18114
    """ Operation """

    RELEASE_ID = 18115

    RELEASE_DESCRIPTION = 18116

    BIDITEM = 18117

    SPECIAL_COMPONENT_FOR_REINFORCEMENT = 18118

    MARK_NO__WITH_INDEX_MESHESBARS_IN_ELEMENT_PLAN = 18119
    """ Mark no. with index (meshes/bars) in element plan """

    MAXIMUM_DIAMETER_OF_OUTER_LAYER_OF_CROSS_BARS = 18120
    """ Maximum diameter of outer layer of cross bars """

    STANDARD_LATTICE_GIRDER_HEIGHT = 18121
    """ Standard lattice girder, height """

    STANDARD_LATTICE_GIRDER_DIAMETER_OF_BOTTOM_BOOM = 18122
    """ Standard lattice girder, diameter of bottom boom """

    STANDARD_LATTICE_GIRDER_DIAMETER_OF_TOP_BOOM = 18123
    """ Standard lattice girder, diameter of top boom """

    REBAR_MARK = 18124

    CO_CLASS = 18125
    """ Part of classification """

    REBAR_PREFIX = 18126

    SUFFIX_CURRENT_LENGTH_UNIT = 18128

    SUFFIX_CURRENT_AREA_UNIT = 18129

    SUFFIX_CURRENT_VOLUME_UNIT = 18130

    SUFFIX_CURRENT_LENGTH_UNIT_MM = 18131

    SUFFIX_CURRENT_LENGTH_UNIT_CM = 18132

    SUFFIX_CURRENT_LENGTH_UNIT_DM = 18133

    SUFFIX_CURRENT_LENGTH_UNIT_M = 18134

    SUFFIX_CURRENT_AREA_UNIT_MM = 18135

    SUFFIX_CURRENT_AREA_UNIT_CM = 18136

    SUFFIX_CURRENT_AREA_UNIT_DM = 18137

    SUFFIX_CURRENT_AREA_UNIT_M = 18138

    SUFFIX_CURRENT_VOLUME_UNIT_MM = 18139

    SUFFIX_CURRENT_VOLUME_UNIT_CM = 18140

    SUFFIX_CURRENT_VOLUME_UNIT_DM = 18141

    SUFFIX_CURRENT_VOLUME_UNIT_M = 18142

    SUFFIX_CURRENT_WEIGHT_UNIT_KG = 18148

    SUFFIX_CURRENT_WEIGHT_UNIT_TO = 18149

    CURRENT_TYPE_OF_LENGTH_UNIT = 18150

    BENDING_DIMENSIONS_ACI_B1 = 18151

    BENDING_DIMENSIONS_ACI_B2 = 18152

    BENDING_DIMENSIONS_ACI_C1 = 18153

    BENDING_DIMENSIONS_ACI_C2 = 18154

    BENDING_DIMENSIONS_ACI_D1 = 18155

    BENDING_DIMENSIONS_ACI_D2 = 18156

    BENDING_DIMENSIONS_ACI_E1 = 18157

    BENDING_DIMENSIONS_ACI_E2 = 18158

    BENDING_DIMENSIONS_ACI_F1 = 18159

    BENDING_DIMENSIONS_ACI_F2 = 18160

    BENDING_DIMENSIONS_ACI_H1 = 18161

    BENDING_DIMENSIONS_ACI_H2 = 18162

    BENDING_DIMENSIONS_ACI_K1 = 18163

    BENDING_DIMENSIONS_ACI_K2 = 18164

    SUPERIMPOSED_LOAD = 18165
    """ Area load on slab """

    LENGTHDM_M = 18171
    """ Length[dm] (m) - string """

    LENGTHMM_M = 18172
    """ Length[mm] (m) - string """

    VARIED_GROUP = 18173

    AXIS_START_POINT_X = 18174

    AXIS_START_POINT_Y = 18175

    AXIS_START_POINT_Z = 18176

    AXIS_END_POINT_X = 18177

    AXIS_END_POINT_Y = 18178

    AXIS_END_POINT_Z = 18179

    OBJECT_ROTATION_ANGLE = 18180

    CUSTOM_CLASSIFICATION_CODE = 18181
    """ For additional classification """

    CUSTOM_CLASSIFICATION_DESCRIPTION = 18182
    """ For additional classification """

    CLASSIFICATION_SOURCE = 18183
    """ For additional classification """

    CLASSIFICATION_EDITION = 18184
    """ For additional classification """

    CLASSIFICATION_EDITION_DATE = 18185
    """ For additional classification """

    CLASSIFICATION_NAME = 18186
    """ For additional classification """

    CLASSIFICATION_DESCRIPTION = 18187
    """ For additional classification """

    CLASSIFICATION_LOCATION = 18188
    """ For additional classification """

    CLASSIFICATION_REFERENCE_TOKENS = 18189
    """ For additional classification """

    DENSITY = 18192
    """ Density """

    MATERIAL_ID = 18193
    """ Material ID """

    MARK_NR_ = 18196
    """ Mark number """

    SCHEME = 18197
    """ Schema for mark number """

    FIRST_NUMBER = 18198
    """ Starting number for mark number """

    CODE = 18199
    """ Material code from Material Catalog """

    CONTROL_CODE = 18200

    BENDING_TYPE = 18201

    CHANGE_ORDER_NO = 18202

    CHANGE_ORDER_DESCRIPTION = 18203

    RFI_NO = 18204

    RFI_DESCRIPTION = 18205

    REBAR_STATUS = 18206

    BENDING_DIMENSIONS_ACI_B3 = 18207

    BENDING_DIMENSIONS_ACI_B4 = 18208

    BENDING_DIMENSIONS_ACI_C3 = 18209

    BENDING_DIMENSIONS_ACI_C4 = 18210

    BENDING_DIMENSIONS_ACI_D3 = 18211

    BENDING_DIMENSIONS_ACI_D4 = 18212

    BENDING_DIMENSIONS_ACI_E3 = 18213

    BENDING_DIMENSIONS_ACI_E4 = 18214

    BENDING_DIMENSIONS_ACI_F3 = 18215

    BENDING_DIMENSIONS_ACI_F4 = 18216

    BENDING_DIMENSIONS_ACI_H3 = 18217

    BENDING_DIMENSIONS_ACI_K3 = 18218

    BENDING_DIMENSIONS_ACI_J1 = 18219

    BENDING_DIMENSIONS_ACI_J2 = 18220

    BENDING_DIMENSIONS_ACI_J3 = 18221

    REFERENCE = 18222
    """ IFC-Reference """

    START_END_PREP = 18226

    END_END_PREP = 18227

    DEFINITION_BUILDING_SYSTEM = 18231
    """ Definition of group by which building elements are grouped according to a common function within the building. """

    DEFINITION_OF_BUILDING_SERVICES = 18232
    """ Definition of distribution system groups, designed to receive, store, maintain, distribute, or control the flow of a distribution media. """

    BUILDING_SYSTEM = 18233
    """ Assignments of group by which building elements are grouped according to a common function within the building. """

    BUILDING_SERVICES = 18234
    """ Distribution system group assignments, designed to receive, store, maintain, distribute, or control the flow of a distribution media. """

    DEFINITION_GROUP = 18235
    """ Definition of of any arbitrary group. """

    GROUP = 18236
    """ Assignments to any arbitrary group. """

    END_MACHINING_ABBREVIATION = 18237

    CLEAR_WIDTH = 18238
    """ Actual clear width measured as the clear space for accessibility and egress. """

    COUNTERCLINE = 18239
    """ Sloping angle of the object, measured perpendicular to the slope - relative to horizontal. """

    MECHANICAL = 18241
    """ dication whether the element is operated machanically or not. """

    RADIATION_TRANSMITTANCE = 18242
    """ The ratio of incident solar radiation that directly passes through a shading system. """

    RADIATION_REFLECTANCE = 18243
    """ The ratio of incident solar radiation that is reflected by a shading system. """

    TRANSMITTANCE_FOR_VISIBLE_LIGHT = 18244
    """ Fraction of the visible light that passes the shading system at normal incidence. """

    REFLECTANCE_FOR_VISIBLE_LIGHT = 18245
    """ Fraction of the visible light that is reflected by the glazing at normal incidence. """

    SURFACE_ROUGHNESS = 18246
    """ A measure of the vertical deviations of the surface. """

    SURFACE_COLOR = 18247
    """ The color of the surface. """

    SUNSHADE_TYPE = 18248

    BUILDING_IDENTIFIER_PERMANENT = 18249
    """ Indicates whether the identity assigned to a building is permanent or temporary. """

    TYPE_OF_EXECUTION = 18250

    BUILDING_CLASS_FIRE_PROTECTION = 18251
    """ Main fire protection class for the building which is assigned from the fire protection classification table as given by the relevant national building code. """

    LAST_YEAR_OF_RENOVATION = 18252
    """ Year of last major refurbishment, or reconstruction, of the building. """

    MONUMENT_PROTECTION = 18253
    """ This builing is listed as a historic building. """

    SITE_OCCUPANCY_INDEX = 18254
    """ The ratio of the utilization, TotalArea / BuildableArea, expressed as a maximum value. """

    CONSTRUCTION_PHASE = 18256
    """ Construction phase. """

    DEPARTMENT = 18257
    """ Postal Address: An organization defined address for internal mail delivery. """

    ADDRESS_LINE_1 = 18258
    """ Postal Address: First line of address, mostly used for building number and street name. """

    ADDRESS_LINE_2 = 18259
    """ Postal Address: Second, optional line of address, mostly used for aditional specification. """

    POSTAL_BOX = 18260
    """ Postal Address: Postal box. An address that is implied by an identifiable mail drop. """

    TOWN = 18261
    """ Postal Address: The name of a town. """

    REGION = 18262
    """ Postal Address: The name of a region. The counties of the United Kingdom and the states of North America are examples of regions. """

    POSTAL_CODE = 18263
    """ Postal Address: Postal code. The code that is used by the country's postal service. """

    COORDINATE_REFERENCE_SYSTEM = 18264
    """ Name by which the coordinate reference system is identified. """

    SURVEY_POINT_RIGHT_VALUE = 18265
    """ Specifies the location along the easting of the coordinate system of the target map coordinate reference system.  """

    SURVEY_POINT_HEIGHT_VALUE = 18266
    """ Specifies the location along the northing of the coordinate system of the target map coordinate reference system.  """

    SURVEY_POINT_HEIGHT = 18267
    """ Orthogonal height relative to the vertical datum specified.  """

    SURVEY_POINT_ANGLE = 18268
    """ Specifies the rotation angle of the target map coordinate reference system.  """

    STYLE = 18269
    """ Furniture style description. """

    NOMINAL_HEIGHT = 18270
    """ Indication of the nominal height of the object.  """

    NOMINAL_LENGTH = 18271
    """ Determines the nominal or specified length of the object.  """

    NOMINAL_DEPTH = 18272
    """ Determines the nominal depth or specified depth of the object.  """

    MAIN_COLOR = 18273
    """ Indication of the main color of this type of furniture.  """

    BUILT_IN = 18274
    """ Indication whether the furniture type is built-in (TRUE) or not (FALSE).  """

    USED = 18275
    """ Indication whether the element is integrated into a workstation (TRUE) or not (FALSE).  """

    GROUP_NUMBER = 18276
    """ Indication of the group number, e.g. for panels, work surfaces, storage, etc.  """

    NOMINAL_WIDTH = 18277
    """ Indication of the nominal width of the object.  """

    SURFACE_TREATMENT = 18278
    """ Specifying the surface treatment of the system furniture elements of this type, such as 'walnut' or 'fabric'.  """

    SAFETY_STANDARD = 18279
    """ Safety standard (BG Bau) """

    LOAD_CLASS = 18280
    """ Load class (BG Bau) """

    WIDTH_CLASS = 18281
    """ Width class (BG Bau) """

    BRAND = 18283
    """ Brand name (Leviat, general) """

    HOMEPAGE_DEVELOPER = 18284
    """ Homepage developer (Leviat, general) """

    CERTIFICATES = 18285
    """ Certificates (Leviat, general) """

    STANDARDS = 18286
    """ Standards (Leviat, general) """

    COPYRIGHT = 18287
    """ Copyright (Leviat, general) """

    MANHOLE_INLET_4 = 18288
    """ Manhole inlet 4 """

    MANHOLE_INLET_5 = 18289
    """ Manhole inlet 5 """

    MANHOLE_INLET_6 = 18290
    """ Manhole inlet 6 """

    MANHOLE_INLET_7 = 18291
    """ Manhole inlet 7 """

    MANHOLE_INLET_8 = 18292
    """ Manhole inlet 8 """

    MANHOLE_INLET_9 = 18293
    """ Manhole inlet 9 """

    WINDOW_TYPE = 18294
    """ Window type """

    SURFACE_WEATHERBOARD = 18295
    """ Surface weatherboard """

    BASE_MATERIAL = 18296
    """ Specification about the material in which the window will be fixed """

    WHEELCHAIR_RAMP = 18297
    """ Threshold wheelchair ramp available """

    TG_INSIDE = 18298
    """ Specification tempered glass inside """

    LSG_INSIDE = 18299
    """ Specification laminated safety glass inside """

    LSG_OUTSIDE = 18300
    """ Specification laminated safety glass outside """

    MAP_PROJECTION = 18301
    """ Name by which the map projection is identified, e.g. 'UTM', 'Gaus-Krueger'. """

    MAP_ZONE = 18302
    """ Name by which the map zone, relating to the MAP_PROJECTION, is identified, like '32' for UTM32. """

    MAP_UNIT = 18303
    """ Length unit of the coordinate axes composing the map coordinate system. """

    DATE__TIME_ORDERED = 18304

    DATE__TIME_SHEARED = 18305

    DATE__TIME_BENT = 18306

    DATE__TIME_THREADED = 18307

    DATE__TIME_LOADED = 18308

    DATE__TIME_SHIPPED = 18309

    DATE__TIME_PLACED = 18310

    LOADER_ID = 18311

    UNLOADER_ID = 18312

    ATTRIBUTE_SET_CATEGORY = 18313
    """ Attribute set category to link attribute set """

    EMPTY_DRILLING = 18315
    """ Civil engineering/excavation pit """

    DRILLING_METHOD = 18316
    """ Civil engineering/excavation pit """

    VIEW_AREA = 18317
    """ Civil engineering/excavation pit """

    REINFORCED = 18318
    """ Civil engineering/excavation pit """

    VIEW_PLANE = 18319
    """ Civil engineering/excavation pit """

    MAXIMUM_GRAIN_SIZE = 18320
    """ Maximum grain concrete """

    STEEL_GRADE = 18321
    """ Civil engineering/excavation pit """

    BEAM_INSTALLATION = 18322
    """ Civil engineering/excavation pit """

    AXIS_OFFSET = 18323
    """ Civil engineering/excavation pit """

    INSULATION_THICKNESS = 18324
    """ Insulation thickness/thickness """

    G_VALUE = 18325
    """ Total energy transmittance g value """

    UW_VALUE = 18326
    """ Thermal transmittance Uw [W/m2K] """

    UG_VALUE = 18327
    """ Thermal transmittance Ug [W/m2K] """

    UF_VALUE = 18328
    """ Thermal transmittance Uf [W/m2K] """

    UCW_VALUE = 18329
    """ Ucw value [W/m2K] """

    LIGHT_TRANSMITTANCE = 18330
    """ Light transmittance """

    SPECTRUM_MATCHING_VALUE_C = 18331
    """ Spectrum matching value C (sound absorption) """

    SPECTRUM_MATCHING_VALUE_CTR = 18332
    """ Spectrum matching value Ctr  """

    IMPOSED_LOAD = 18333
    """ Imposed load """

    AMOUNT_OF_WORK = 18334
    """ Amount of work """

    CONSISTENCY_CLASS = 18335
    """ Consistency class """

    MASONRY_BEARING = 18336
    """ Masonry bearing """

    E_MODULE = 18337
    """ E-module """

    SHRINKAGE_DIMENSION = 18338
    """ Shrinkage dimension """

    EXPOSED_CONCRETE = 18339
    """ Exposed concrete yes/no """

    FOOTSTEP_SOUND_LEVEL_REDUCTION = 18340
    """ Footstep sound level reduction """

    SD_VALUE = 18341
    """ Water vapor diffusion equivalent air layer thickness """

    PRACTICAL_DEGREE_OF_SOUND_ABSORPTION = 18342
    """ Rated building sound insulation index R'w """

    RATED_SOUND_ABSORPTION_COEFFICIENT = 18343
    """ Rated building sound insulation index R'w """

    CHLORIDE_CLASS = 18344
    """ Chloride class """

    CHLORIDE_CONTENT = 18345
    """ Chloride content in percent """

    WALLING_TYPE = 18346
    """ Walling type/bond types """

    MARK_NUMBER_TEXT = 18347
    """ Mark number in text format """

    XPLAN_VERSION = 18352
    """ Project attribute: XPlan version (5.3, 4.1, ...) """

    XPLAN_CLASS = 18353
    """ Project attribute: XPlan class (BP_Plan, FP_Plan, RP_Plan, LP_Plan, SO_Plan) """

    XPLAN_ATTRIBUTES = 18354
    """ Project attribute: XPlan attributes """

    XPLAN_OBJECT_VERSION = 18355
    """ XPlan version (5.3, 4.1, ...) """

    XPLAN_OBJECT = 18356
    """ XPlan object type (any BP_.., FP_.., ...) """

    XPLAN_OBJECT_ATTRIBUTES = 18357
    """ XPlan object attributes """

    ATTRIBUTE_SET_OBJECT = 18358
    """ Attribute set object to link attribute set """

    XPLAN_COORDINATE_SYSTEM = 18362
    """ Project attribute: XPlan coordination system (EPSG code) """

    GROUTING_LINE = 18363
    """ Civil engineering/excavation pit """

    FREE_LENGTH_SYSTEM = 18364
    """ Civil engineering/excavation pit """

    LIFE_CYCLE = 18365
    """ Civil engineering/excavation pit """

    VERTICAL_INCLINATION = 18366
    """ Civil engineering/excavation pit """

    HORIZONTAL_INCLINATION = 18367
    """ Civil engineering/excavation pit """

    CHARACTERISTIC_ANCHORING_FORCE = 18368
    """ Civil engineering/excavation pit """

    TEST_FORCE = 18369
    """ Civil engineering/excavation pit """

    CLAMPING_FORCE = 18370
    """ Civil engineering/excavation pit """

    ULTIMATE_LOAD = 18371
    """ Civil engineering/excavation pit """

    LOAD_AT_YIELD_STRENGTH = 18372
    """ Civil engineering/excavation pit """

    NUMBER_OF_STRANDS = 18373
    """ Civil engineering/excavation pit """

    STRAND_DIAMETER = 18374
    """ Civil engineering/excavation pit """

    BEAM_DIAMETER = 18375
    """ Civil engineering/excavation pit """

    REMOVABLE = 18376
    """ Civil engineering/excavation pit """

    REGROUT = 18377
    """ Civil engineering/excavation pit """

    PRESTRESSED = 18378
    """ Civil engineering/excavation pit """

    ANCHOR_TYPE = 18379
    """ Civil engineering/excavation pit """

    CORROSION_PROTECTION = 18380
    """ Civil engineering/excavation pit """

    STEEL_GRADE_TENSION_MEMBER = 18381
    """ Civil engineering/excavation pit """

    MATERIAL_GROUT_BODY = 18382
    """ Civil engineering/excavation pit """

    ANCHOR_LOCATION = 18383
    """ Civil engineering/excavation pit """

    SCOPE = 18384
    """ Civil engineering/excavation pit """

    DRILLING_DIAMETER = 18385
    """ Civil engineering/excavation pit """

    DOUBLE_PROFILE_GAP = 18387
    """ Double profile gap """

    HEIGHT_IFC = 18392

    DIAMETER_IFC = 18393

    CLASH_FLAG = 18400

    CLASH_NUMBER = 18401

    CLASH_TYPE = 18402

    CLASH_DEPTH = 18403

    CLASH_PRIORITY = 18404

    CLASH_DATE_TIME = 18405

    CLASH_COMPONENT_A_GUID = 18406

    CLASH_COMPONENT_B_GUID = 18407

    CLASH_COMPONENT_A_DRAWING_FILE = 18408

    CLASH_COMPONENT_B_DRAWING_FILE = 18409

    CLASH_COMPONENT_A_OBJECT_NAME = 18410

    CLASH_COMPONENT_B_OBJECT_NAME = 18411

    CLASH_STATUS = 18412

    CLASH_DEPTH_TOLERANCE_HARD_CLASH = 18413

    CLASH_DEPTH_TOLERANCE_SOFT_CLASH = 18414

    CLASH_COMPONENTS = 18415

    CUT = 18417
    """ Civil engineering/excavation pit """

    FILL = 18418
    """ Civil engineering/excavation pit """

    CONSTRAINED_MODULUS = 18419
    """ Civil engineering/excavation pit """

    INNER_FRICTION_ANGLE = 18420
    """ Civil engineering/excavation pit """

    WET_UNIT_WEIGHT_OF_SOIL = 18421
    """ Civil engineering/excavation pit """

    UNIT_WEIGHT_OF_SOIL = 18422
    """ Civil engineering/excavation pit """

    UNDRAINED_COHESION = 18423
    """ Civil engineering/excavation pit """

    DRAINED_COHESION = 18424
    """ Civil engineering/excavation pit """

    DOUBLE_PROFILE_CONFIGURATION = 18425
    """ Double profile configuration """

    BOLT_FRICTION_BEARING_CONDITION = 18427

    FIELD_BOLTED = 18428
    """ Steel bolt is bolted on-construction-site """

    TENSION_CONTROLLED_BOLT = 18429

    FIELD_WELDED = 18430
    """ Welding is done on-construction-site """

    STITCHED_WELD = 18431

    WELD_ALL_AROUND = 18432

    PREQUALIFIED_WELD_TAIL_POSITION = 18433

    PREQUALIFIED_WELD_TAIL_PROCESS = 18434

    PREQUALIFIED_WELD_TAIL_TEXT = 18435

    WELD_ROOT_FACE = 18436

    WELD_ROOT_OPENING = 18437

    WELD_SETBACK_LEFT = 18438

    WELD_SETBACK_RIGHT = 18439

    WELD_CONTOUR = 18440

    USE_FILLET_BACKUP_WELD = 18441

    WELD_STITCH_LENGTH = 18442

    WELD_STITCH_SPACING = 18443

    WELD_STITCH_TERMINATION_LEFT = 18444

    WELD_STITCH_TERMINATION_RIGHT = 18445

    MATERIAL_USE = 18446

    AUSSCHREIBEN_DE = 18447
    """ Attribute for connection to ausschreiben.de """

    BENDING_DIMENSIONS_BS8666_A_R = 18461

    BENDING_DIMENSIONS_BS8666_A = 18462

    BENDING_DIMENSIONS_BS8666_B = 18463

    BENDING_DIMENSIONS_BS8666_C = 18464

    BENDING_DIMENSIONS_BS8666_D = 18465

    BENDING_DIMENSIONS_BS8666_E = 18466

    BENDING_DIMENSIONS_BS8666_F = 18467

    BENDING_DIMENSIONS_BS8666_R = 18468

    FORM_OF_DELIVERY = 18469
    """ Form of delivery """

    MOMENT_OF_INERTIA = 18470
    """ Moment of inertia """

    ELASTIC_SECTION_MODULUS = 18471
    """ Elastic section modulus """

    PLASTIC_SECTION_MODULUS = 18472
    """ Plastic section modulus """

    STATIC_MOMENT = 18473
    """ Static moment """

    COATING_AREA = 18474
    """ Coating area """

    LCA_CLASS = 18476
    """ OneClick Life Cycle Assessment Class """

    LCA_TRANSPORT_DISTANCE = 18477
    """ LCA transport distance in kilometers """

    SYSTEM = 18479

    COST_GROUP = 18490
    """ for example DIN 276 classification """
