#!/usr/bin/env ruby

require 'optparse'
require 'test/unit'
require 'tmpdir'

require 'mail'
require 'maildir'
require 'maildir/subdirs'
require 'maildir/serializer/mail'

Maildir::Message.serializer = Maildir::Serializer::Mail.new

# http://rubydoc.info/gems/maildir/1.0.0/frames
# env RUBYOPT=rubygems ruby ~/src/lpth/maildirfilter.rb

def list_all(mailbox)
	mailbox.list(:new) + mailbox.list(:cur)
end

def open_maildir(path)
	mailbox = Maildir.new(path, create=false)
	raise 'invalid mailbox' unless File.directory?(mailbox.path)
	mailbox
end

def get_mailbox(mailbox, dir)
	open_maildir(mailbox.path + dir)
end

def should_copy(mail, mailbox)
	mailbox and not ['list', 'bulk'].include?(mail['Precedence'].to_s) and
		not list_all(mailbox).any? {|existing| mail.message_id == existing.data.message_id}
end

def get_domains(mail)
	addresses = mail.destinations + mail.from_addrs
	addresses.map {|address| address.split('@', 2).last}
end

def make_shared(src, dst, domain_to_dir, dryrun)
	
	p 'make_shared'
	
	seen = []
	list_all(src).each do |mail|
		#p mail.flags
		mail = mail.data
		if seen.include?(mail.message_id)
			break # in case of duplicates in mailbox
		end
		seen << mail.message_id
		domains = get_domains(mail) & domain_to_dir.keys
		# puts mail.message_id, domains
		domains.each do |domain|
			mailbox = get_mailbox(dst, domain_to_dir[domain])
			if should_copy(mail, mailbox)
				if dryrun
					puts "copying '#{mail.subject}'(#{mail.message_id}) to #{mailbox.path}"
				else
					mailbox.add(mail).process
				end
			end
		end
	end
end

class TestFilter < Test::Unit::TestCase

	def test_filter
		Dir.mktmpdir do |dir|
			maildir = Maildir.new("#{dir}/maildir")
			mail = Mail.new do
				from('user@example.org')
				to('User <user@example.com>')
				subject('Inbox test')
				body('inbox test')
				ready_to_send! # add msg id
			end
			maildir.add(mail)
			list_mail = Mail.new do
				from('user@example.org')
				to('user@example.com')
				subject('Inbox test')
				body('inbox test')
				header('Precedence: list')
				ready_to_send! # add msg id
			end
			maildir.add(list_mail)
			sent = maildir.create_subdir('Sent Items')
			sent_mail = Mail.new do
				from('user@example.com')
				to('user@example.org')
				subject('Inbox test')
				body('inbox test')
				ready_to_send!
			end
			sent.add(sent_mail)
			
			shared = Maildir.new("#{dir}/shared")
			clients = shared.create_subdir('Clients')
			# library seems to be broken for creating sub sub directories
			example_shared = Maildir.new(clients.path.sub(/\/$/, '') + '.Example Co')
			# example_shared = client_shared.create_subdir('Example Co')
			# puts 'lkj', shared.subdirs(only_direct=false).inspect

			# die

			domain_to_dir = {'example.com'=>'.Clients.Example Co'}
			make_shared(maildir, shared, domain_to_dir, false)
			make_shared(sent, shared, domain_to_dir, false)

			# puts `find #{dir}`
			assert_equal(example_shared.list(:cur).size, 2) 
		end
	end
end

def main
	options = {}
  	OptionParser.new do |opts|
    	opts.banner = "Usage: #{$PROGRAM_NAME} [options] src ... dst"
    	opts.separator ''
    	opts.on('--dryrun', 'Just print what would do') do |dryrun|
    		options[:dryrun] = dryrun
    	end
        opts.on_tail("-h", "--help", "-H", "Display this help message.") do
          puts opts
          exit
        end
	    # opts.on("-v", "--[no-]verbose", "Run verbosely") do |v|
	    #     		options[:verbose] = v
	    #     	end
	  	if ARGV.size == 0:
	  		puts opts
	  		exit
	  	end
  	end.parse!
  	
  	srcs = ARGV.clone
  	dst = srcs.pop
  	
	domain_to_dir = {'made.com'=>'.Clients.Made'}
  	srcs.each do |src|
		make_shared(open_maildir(src),
					open_maildir(dst),
					domain_to_dir, options[:dryrun])
  	end
  	
  	
end


if __FILE__ == $PROGRAM_NAME
  	main
end
