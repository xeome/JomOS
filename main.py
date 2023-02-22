import utils
import tweaks

configuration = utils.parse_cli_arguments()

# Check if DRYRUN mode is on
if configuration["DRY_RUN"]:
    utils.log.info("DRYRUN mode is on")

# Read files
GENERIC = utils.read_file_lines("scripts/generic")
THEMING = utils.read_file_lines("scripts/theming")
REPOS = utils.read_file_lines("scripts/repos")

system_info = tweaks.get_system_info()
zram_state = utils.get_zram_state()
zswap_state = utils.get_zswap_state()

# Get user input and confirm to proceed
utils.confirm_to_proceed()

utils.log.info(
    f'USERNAME: "{system_info["username"]}"\nRAM AMOUNT: {system_info["phys_mem_gb"]}\nCALCULATED SWAPPINESS: {system_info["swappiness"]}\nCALCULATED '
    f"VFS_CACHE_PRESSURE: {system_info['vfs_cache_pressure']}"
)

# Copy configs from system to ./etc for modification
utils.copy_configs()

# Modify configs in ./etc that were copied from system
utils.modify_configs()

# Apply tweaks if not in DRYRUN mode and according to configuration
utils.apply_tweaks(configuration, GENERIC, THEMING, REPOS, system_info)
