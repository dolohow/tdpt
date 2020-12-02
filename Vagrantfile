Vagrant.configure("2") do |config|
  config.vm.box = "generic/ubuntu2004"
  config.vm.synced_folder "./", "/vagrant", type: "nfs", nfs_version: 4, linux__nfs_options: ['rw', 'no_root_squash']
end
