#!/usr/bin/env ruby

require 'optparse'
# require 'test/unit'
require 'tmpdir'

require 'net/imap'
#require 'ruby-debug'
require 'set'
require 'yaml'

class MailCopier
  def initialize
    file = File.new(File.expand_path('~/.imapdirfilter.yaml'))
    if (file.stat.mode & 044) != 0
      raise 'config should not be world readable'
    end
    config = YAML.load(file)
    @mailboxes = config['mailboxes']
    file.close
    #Net::IMAP.debug = true
    port = Net::IMAP::PORT
    certs = nil
    usessl = false
    verify = false
    if config['ca_file']
      port = 993
      certs = config['ca_file']
      usessl = true
      verify = true
    end
    @imap = Net::IMAP.new(config['server'], port, usessl, certs, verify)
    @imap.login(config['user'], config['password'])
    @message_id_cache = Hash.new { |hash, key| hash[key] = Set.new }
  end

  def list
    @imap.list('', '*').each do |mailbox|
      puts mailbox
    end
  end

  def process(src_mailbox, dryrun, limit)
    count = 0
    return count if limit and count >= limit
    get_envelopes(src_mailbox).each do |data|
      envelope = data.attr['ENVELOPE']
      # debugger
      dst_mailbox = get_mailbox(envelope)
      if dst_mailbox
        if copy_new_mail(data, src_mailbox, dst_mailbox, dryrun)
          count += 1
        end
      end
      break if limit and count >= limit
    end
    return count
  end

  def get_envelopes(mailbox)
    @imap.examine(mailbox)
    if @imap.responses["EXISTS"][-1] > 0
      @imap.fetch(1..-1, 'ENVELOPE')
    else
      []
    end
  end
  
  def get_mailbox(envelope)
    addresses = []
    addresses += envelope.from if envelope.from
    addresses += envelope.to if envelope.to 
    addresses += envelope.cc if envelope.cc
    addresses.each do |address|
      if @mailboxes.include?(address.host)
        return @mailboxes[address.host]
      end
    end
    return nil
  end
  
  def copy_new_mail(fetchdata, src_mailbox, dst_mailbox, dryrun)
    if not @message_id_cache.include?(dst_mailbox)
      get_envelopes(dst_mailbox).each do |data|
        envelope = data.attr['ENVELOPE']
        @message_id_cache[dst_mailbox].add(envelope.message_id)
      end
    end
    
    copied = false
    envelope = fetchdata.attr['ENVELOPE']
    message_id = envelope.message_id
    #Precedence: bulk
    #puts "copy_new_mail #{message_id} #{mailbox} #{@message_id_cache[mailbox].include?(message_id)}"
    if not @message_id_cache[dst_mailbox].include?(message_id)
      @imap.select(src_mailbox)
      headers = @imap.fetch(fetchdata.seqno, 'RFC822.HEADER')[0].attr['RFC822.HEADER']
      if headers.include?("\nPrecedence: bulk\r")
      else
        puts "copying #{src_mailbox} '#{envelope.subject}' to #{dst_mailbox}"
        if @imap.fetch(fetchdata.seqno, 'ENVELOPE')[0].attr['ENVELOPE'].message_id == message_id
          if not dryrun
            @imap.copy(fetchdata.seqno, dst_mailbox)
            copied = true
          end
        else
          raise 'unexpected message_id'
        end
      end
    end
    @message_id_cache[dst_mailbox].add(message_id)
    return copied
  end
end

def main
  options = {:dryrun => false,
             :single => false}
  limit = false
  OptionParser.new do |opts|
    opts.banner = "Usage: #{$PROGRAM_NAME} [options] src ... dst"
    opts.separator ''
    opts.on('--dryrun', 'Just print what would do') do |dryrun|
      options[:dryrun] = dryrun
    end
    opts.on('--single', 'Copy only one email') do |single|
      limit = 5
    end
    opts.on_tail("-h", "--help", "-H", "Display this help message.") do
      puts opts
      exit
    end
  end.parse!
  copier = MailCopier.new
  # copier.list
  count = 0
  
  ['INBOX', 'Sent Items', 'Sent'].each do |mailbox|
    count += copier.process(mailbox, options[:dryrun], limit)
    limit -= count if limit
  end
end

if __FILE__ == $PROGRAM_NAME
  main
end
