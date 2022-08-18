known_lib_list = [
    'asm','asciitable','airline','args4j','Apache Aurora','ADT4J','auto','ANTLR','Apache Avro','Apache Orc','Apache Parquet','Apache Thrift',
    'Apache Calcite','Apache Drill','Apache Maven', 'Apache Phoenix', 'ArangoDB', 'Almanac Converter','Apache DeltaSpike','AspectJ','Apache Geode'
    'Apache Storm','Apache ZooKeeper','Atomix','Axon','Atomikos','Artipie','Apache POI','Apache SIS','Agrona','Apache HttpComponents','Async Http Client'
    'bazel','buck','bytebuddy','Bootify','BoofCV','Bigqueue','bytecode viewer', 'Byteman', 'Big Queue','Bitronix','Boxfuse'
    'cache2k','concurrent','cglib','caffeine','checkstyle','clover','Cobertura','centraldogma','cfg4j','config','Configurate','choco', 'Chronicle Map',
    'Capsule','Central Repository','Cloudsmith','Cassandre','CATG','Checker Framework','Cyclops','ClassGraph'
    'dom4j','doov','dotenv', 'Debezium', 'druid', 'Dagger','DCEVM','Dropwizard Circuit Breaker','documents4j','docx4j','Daikon','derive4j','Disruptor'
    'ehcache','Error Prone','Externalized Properties', 'eXist','Eclipse Collections','Eclipse'
    'FreeBuilder','fastcsv', 'FlexyPool','Flyway','Feather','Faux Pas','Failsafe','fastexcel','Fugue','Functional Java','FXGL','fastutil','Feign'
    'gradle','Geci','Governator','Guice','Getdown','Geo','GeoTools','GraphHopper','Google HTTP Client'
    'HyperMinHash java', 'H2','HikariCP','HK2','HotswapAgent','Hazelcast','H2GIS','HPPC','hate'
    'infinispan','infer','immutables','imageJ','ini4j','iCal4j','IzPack','IntelliJ IDEA','Imgscalr','image comparison'
    'junit', 'junitperf', 'jarjar', 'jmapper','jrexx','javassist','jansi','Java ASCII Render','jcommander','jbock','JavaParser','JCTools'
    'jexer','jline','JOpt Simple','jQAssistant','JaCoCo','JavaPoet','JHipster','Joda Beans','JPABuddy','JavaCC','JFlex','JavaSymbolSolver'
    'javaCV','jacop','jackson dataformat csv','JDBI','Jedis','Jest','jetcd','Jinq','jOOQ','Jollyday','JayWire','JGroups','JavaPackager',
    'jDeploy','jlink.online','Java Path Finder','JMLOK','jOOλ','JBox2D','jMonkeyEngine','Jgeohash','JavaFX','JSON LD','jGRASP','jOOR'
    'KAConf','KeY','Koloboke'
    'lanterna','lombok','Leaf','Liquibase','libGDX','Litiengine','LWJGL'
    'maven','mapstruct','modulemapper','mixin','microconfig','MapDB','MariaDB4j','Modality','Manifold','Mini2Dx','Mapsforge','methanol','Mirror'
    'NullAway','NoException','Narayana','Nexus','NetBeans'
    'orika','owner','optaplanner','opencsv','OpenJML','Objenesis'
    'perses','picocli','PMD','Persistent Collection','Protobuf','packr','Parity','Philadelphia','protonpack'
    'Querydsl','QueryStream','QuestDB','Quasar'
    'remap','Record Builder','RoaringBitmap','Realm','Redisson','requery','resilience4j','really executable jars maven plugin','restQL java','Retrofit','Ribbon','Riptide'
    'Recaf','ReflectASM','Reflections'
    'selma','singularity','SonarJava','Spoon','Spotbugs','super csv','SBE','Speedment','Spring Data JPA MongoDB Expressions','SneakyThrow','ScaleCube Services'
    'Seata','Square','Stripe','StreamEx','Spatial4j','Scene Builder','SWT','Siren4J'
    'trove','Text IO','Telosys','Tape','Trino','ThreeTen Extra','Time4J','Tail','ta4j','Tess4J','Thumbnailator','TwelveMonkeys'
    'univocity parsers','unirest java'
    'Vibur DBCP','Vavr','Visual Studio Code'
    'Wire',
    'Xodus',
    'Zuul','zerocell','ZXing'
]









'''
import re

module_name_regrex = re.compile(r'\s*([\-a-zA-Z0-9_]*)\-((\d+\.)+\d*)',re.I | re.M | re.S)
module_version_regrex = re.compile(r'([\d+.]*)*',re.I | re.M | re.S)
example = 'jarjar-1.2.6.jar'
module_name = re.search(module_name_regrex,example)
#print(module_name.group(2))
#print(module_name.span(0))
#print(module_name.start(0))
'''
