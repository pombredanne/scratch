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
    config = YAML.load(file)
    file.close
    options = {}
    if config['ssl']
      options[:ssl] = {:verify_mode => OpenSSL::SSL::VERIFY_NONE}
    end
    # Net::IMAP.debug = true
    @imap = Net::IMAP.new(config['server'], options)
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
    mailboxes = {
      'made.com' => 'Public/UK/Sales/Customers/Made dot com',
      'canterbury.ac.uk' => 'Public/UK/Sales/Customers/Canterbury University',
      'enotions.co.uk' => 'Public/UK/Sales/Customers/Enotions',
      'evoture.co.uk' => 'Public/UK/Sales/Customers/Enotions',
      'britglass.co.uk' => 'Public/UK/Sales/Customers/British Glass',
      'sfm-limited.com' => 'Public/UK/Sales/Customers/SFM',
      'virginmedia.co.uk' => 'Public/UK/Sales/Customers/Virgin Media',
    }
#    mailboxes = {
#      'made.com' => 'Public/Clients/Made',
#      'canterbury.ac.uk' => 'Public/Clients/CCCU'
#    }
    addresses.each do |address|
      if mailboxes.include?(address.host)
        return mailboxes[address.host]
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
    # opts.on("-v", "--[no-]verbose", "Run verbosely") do |v|
    #         options[:verbose] = v
    #       end
    # if ARGV.size == 0:
    #   puts opts
    #   exit
    # end
  end.parse!
  copier = MailCopier.new
  # copier.list
  #copier.get_envelopes('INBOX')
  # copier.get_envelopes('Public/Clients/CCCU')
  count = 0
  
  ['INBOX', 'Sent Items'].each do |mailbox|
    count += copier.process(mailbox, options[:dryrun], limit)
    limit -= count if limit
  end
  # copier.process('Public/Clients/Made', true)
  #copier.process('Sent Items', options[:dryrun], options[:single])
end

if __FILE__ == $PROGRAM_NAME
  main
end
