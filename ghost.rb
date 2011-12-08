#!/usr/bin/env ruby

require 'net/telnet'
require 'openssl'
require 'yaml'

class SSLTelnet < Net::Telnet
  def initialize(server, port, context)
    @server = server
    @port = port
    @context = context
  end

  def sock
    socket = TCPSocket.open(@server, @port)
    socket = OpenSSL::SSL::SSLSocket.new(socket, @context)
    socket.sync_close = true
    socket.connect
  end
end

file = File.new(File.expand_path('~/.ghost.yaml'))
if (file.stat.mode & 044) != 0
  raise 'config should not be world readable'
end
config = YAML.load(file)

context = OpenSSL::SSL::SSLContext.new
port = 6697
ssl = SSLTelnet.new(config['server'], port, context)

irc = Net::Telnet::new('Telnetmode' => false,
                       'Prompt' => /^:/,
#                       'Dump_log' => 'ghost.log',
                       'Timeout' => 20,
                       'Proxy' => ssl)

#  pop.cmd('user ' + 'your_username_here') { |c| print c }
#  pop.cmd('pass ' + 'your_password_here') { |c| print c }
#  pop.cmd('list') { |c| print c }

nick = config['ghostnick']
irc.cmd({'String' => "PASS *\nNICK #{nick}\nUSER #{nick} 8 * :#{nick}\n",
              'Match' => Regexp.new("^:#{nick} MODE ")})
RPL_ENDOFWHOIS = 318
puts irc.cmd({'String' => "WHOIS #{config['nick']}",
              'Match' => Regexp.new("^:[.a-z]* #{RPL_ENDOFWHOIS} ")})
puts irc.cmd({'String' => "PRIVMSG nickserv :ghost #{config['nick']} #{config['password']}",
              'Match' => /ghosted/})


