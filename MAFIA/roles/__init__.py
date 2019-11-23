from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname("c:/Users/Ernest/Desktop/Mafiabot/Mafiabot-1/MAFIA/roles/baiter"), "*.py"))
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
