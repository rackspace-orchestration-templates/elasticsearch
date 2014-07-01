#
# Cookbook Name:: rax-elasticsearch
# Recipe:: default
#
# Copyright 2014, Rackspace
#
# All rights reserved - Do Not Redistribute
#

node.set[:java][:install_flavor] = 'openjdk'
node.set[:java][:jdk_version] = 7

include_recipe 'java'

# find the first ipv4 address of the cloud network interface
cn_interface_ipv4 = node[:network][:interfaces][:eth2][:addresses].find \
  {|addr, addr_info| addr_info[:family] == "inet"}.first

Chef::Log.info("print interface ip is #{cn_interface_ipv4}")

node.set[:elasticsearch][:custom_config] = {
  'discovery.zen.ping.multicast.address' => cn_interface_ipv4,
  'network.publish_host' => cn_interface_ipv4
  }

include_recipe 'firewall::default'

firewall 'ufw' do
  action :enable
end

firewall_rule 'elasticsearch_intracluster' do
  interface 'eth2'
  action    :allow
end

firewall_rule 'elasticsearch_proxy' do
  port      8080
  action    :allow
end

firewall_rule 'ssh' do
  port      22
  action    :allow
end


include_recipe 'elasticsearch::default'
include_recipe 'elasticsearch::proxy'
