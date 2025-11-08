

import glob
from .BaseCommand import BaseCommand


class BatchRenderSU(BaseCommand):

    def process(self, args):

        rv = {}
        globout = []
        if (args.scene_files != "_"):
            globout = glob.glob(args.scene_files, recursive=True)

        rv['scene_files'] = globout
        args.scene_files = rv
        
        super().process(args)

    
