import argparse
import json
import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger("Launcher")

class Launcher:
    """
    Launcher class for calling dq to launch train.py with each entry in a  
    list of hyperparameters
    """
    def __init__(self, default_config, param, experiment_name):
        """
        :param default_config: the default config file
        :param param: the parameters to be overridden in the base config
                     (these are the hyper parameters we search on and output 
                      path)
        :param experiment_name: name of the experiment
        """
        
        output_dir = default_config.get("io").get("output_save_path")
        output_dir = os.path.join( output_dir, experiment_name)

        override_config = default_config
        logger.debug("override cfg starts as " + str(override_config))
        
        ctr = 0
        p_name = param.get("name")
#for p_name in param.get("value"):
#            logger.debug("Hyper param: " + str(p_name))
            
        #TODO not tested for more than one hyperparams list
        for k, v in override_config.items():
            if k == p_name:
                logger.debug ("Found " + str(p_name) + " : " + str(v))
                for i in param.get("value"):
                    override_config[k] = i 
                    #self.search_and_replace_dict(v, p_name), val)
        
                    o_dir_exp = self.get_op_path(output_dir, p_name, ctr)
                    o_cfg_path = os.path.join(o_dir_exp, "override.cfg")
                    ctr += 1
                    override_config['io']['output_save_path'] = o_dir_exp
        
                    logger.info("Creating " + str(o_dir_exp))
                    path = Path(o_dir_exp)
                    path.mkdir(parents=True)
                    
                    with open(o_cfg_path, 'w') as fp:
                        json.dump(override_config, fp)

                    #call dq TODO
                    DQ_CFG = o_cfg_path
                    logger.info ("Launching DQ_CFG=%s dq-submit dq-launch.sh"%o_cfg_path)
                    os.system("DQ_CFG=%s dq-submit dq-launch.sh"%o_cfg_path)


    def get_op_path(self, output_dir, param_name, val):
        dr = os.path.join(output_dir , param_name + "_" + str(val))
        logger.debug("dir: " + str(dr))
        return dr
   

#    #TODO: refactor later
#    def search_and_replace_dict(self, cfg, param, val):
#        if isinstance(cfg, dict):
#            for k, v in cfg.items():
#                
#                # is a dict itself
#                if isinstance(v, dict):
#                    if k == param:
#                        print("Found "+ str(k) + " : " + str(cfg[k]))
#                        cfg[k] = val
#                        print("Replaced to " + str(cfg[k]))
#                        return
#                    else:
#                        return self.search_and_replace_dict(v, param, val)
#                
#        return



def get_default_config():
    retVal = {
	"seed" : 4337,
	"data" : { "path" : "/deep/group/med/alivecor/training2017", "seed" : 2016 },
	"optimizer" : { "name": "momentum", "epochs" : 50, "learning_rate" : 1e-2,
	    "momentum" : 0.95, "decay_rate" : 1.0, "decay_steps" : 2000
	},
	"model" : { "dropout" : 0.5, "batch_size" : 32,
	    "conv_layers" : [
		{ "filter_size" : 256, "num_filters" : 64, "stride" : 7 },
		{ "filter_size" : 128, "num_filters" : 64, "stride" : 7 }
	   ] },
	"io" : {
	    "output_save_path" : "/tmp"
	}
    }
    return retVal


def main():
    parser = argparse.ArgumentParser(description="Launcher")
    parser.add_argument("-v", "--verbose", default=False, action="store_true")
    parser.add_argument("-e", "--experiment_name", default=None)
    parser.add_argument("-b", "--base_config", default=None)
    parser.add_argument("-p", "--parameter_config", default=None)

    parsed_arguments = parser.parse_args()
    arguments = vars(parsed_arguments)

    is_verbose       = arguments['verbose']
    base_config      = arguments['base_config']
    param_config     = arguments['parameter_config']
    experiment_name  = arguments['experiment_name'].rstrip()

    if is_verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    

    default_config = {}
    param          = {}
    if not base_config:
        default_config = get_default_config()
        logger.debug("No base cfg supplied, so using default - " + str(base_config))
    else:
        with open(base_config) as fid:
            default_config = json.load(fid)
    
    if not param_config:
        raise ValueError("Mandatory to specify parameter config")
    else:
        with open(param_config) as fid:
            param = json.load(fid)
    
    if not experiment_name:
        raise ValueError("Mandatory to specify experiment name")

    launcher = Launcher(default_config, param, experiment_name)



if __name__ == '__main__':
    main()

