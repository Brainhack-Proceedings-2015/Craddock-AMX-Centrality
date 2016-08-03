
# coding: utf-8

# In[158]:

import yaml
import latex




# In[159]:

def replace_latex( fix_strs, citations, labels, inpath ):
    
    import re
    import glob
    
    # regular expression for finding latex command
    ltx_cmd=re.compile('(\w*){(\S*)}(\[*\S*\]*)')
    
    new_strs = []
    list_char = '*'
    figure_env = False
    this_is_caption = False
    figure_file = []
    figure_caption = []
    
    for fix_str in fix_strs:

        if figure_env:
            if not figure_file:
                ff = re.search(r"\\includegraphics\[.*\]\{(.*)\}", fix_str)
                if ff:
                    n = ff.groups()[0]
                    img_files=[f for f in glob.glob(os.path.join(inpath,n+'*')) if 'png' in f or 'pdf' in f or 'jpg' in f]
                    figure_file=img_files[0]
                    continue
            if not figure_caption:
                if "\caption{" in fix_str:
                    fix_str=fix_str.replace("\caption{","")
                    n=fix_str.rfind("}")
                    fix_str=fix_str[:n]+fix_str[n+1:]
                    this_is_caption=True
                    
        new_str = fix_str                    
        for (cmd,op,op2) in ltx_cmd.findall(fix_str):
            outstr=[]
            opns=op.replace('\s','')
            if "label" in cmd:
                labels.append(opns)
                outstr='Figure %d. '%(labels.index(opns)+1)
            elif "ref" in cmd:
                if opns not in labels:
                    labels.append(opns)
                outstr='Fig. %d '%(labels.index(opns)+1)
            elif "cite" in cmd:
                if opns not in citations:
                    citations.append(opns)
                outstr='[%d]'%(citations.index(opns)+1)
            elif "emph" in cmd:
                outstr='*%s*'%(op)
            elif "texttt" in cmd:
                outstr='`%s`'%(op)
            elif "url" in cmd:
                outstr=op
            elif "begin" in cmd:
                if "itemize" in op:
                    list_char = '*'
                elif "enumerate" in op:
                    list_char = '1'
                elif "figure" in op:
                    figure_env = True 
                outstr=' '
            elif "end" in cmd:
                if "figure" in op:
                    figure_env = False
                    outstr='![%s](%s)'%(figure_caption.rstrip(),figure_file)
                else:
                    outstr = ' '
            elif "vspace" in cmd:
                outstr='\n'
            else:
                outstr='\%s{%s}'%(cmd,op)
                print outstr
                
            if outstr:
                new_str = new_str.replace('\%s{%s}%s'%(cmd,op,op2),outstr)
        
        new_str = new_str.replace("\item", list_char)
        new_str = new_str.replace("\\noindent", '')
        new_str = new_str.replace("$", '')
        new_str = new_str.replace("\times", 'x')
            
        if this_is_caption:
            figure_caption = new_str
            this_is_caption = False
        else:
            new_strs.append(new_str)
           
    return(new_strs)


if __name__ == "__main__":
    import argparse
    import os
    parser = argparse.ArgumentParser()

    # basic arguments
    parser.add_argument("input", type=str,
                        help="the markdown input file")
    parser.add_argument("output", type=str,
                        help="the markdown output file")
 
    args = parser.parse_args()
 
    citations=[]
    labels=[]
    
    with open(args.input, 'r') as stream:
        ystr=stream.readlines()

    head_end=ystr.index('...\n')

    head_str=''.join(ystr[0:head_end])
    body=ystr[head_end+1:]

    try:
        header=yaml.load(head_str)
    except yaml.YAMLError as exc:
        print(exc)

    with open(args.output, 'w') as outfd:
        outfd.write("\n")

        # add in the title
        if 'title' in header.keys():
            tmp=header['title'].encode("UTF-8")
        else:
            tmp="Missing Title"
        tmp=" ".join(tmp.split())
        outfd.write(tmp+"\n")
        outfd.write("="*len(tmp)+"\n")
        outfd.write("\n\n")

        # add in the subtitle, the event line
        if 'event' in header.keys():
            tmp="Report from "+header['event'].encode("UTF-8")
        else:
            tmp="Missing Event"
        tmp=" ".join(tmp.split())
        outfd.write(tmp+"\n")
        outfd.write("-"*len(tmp)+"\n")
        outfd.write("\n\n")

        # add in the authors
        tmp=''
        email_str=''
        if 'author' in header.keys():
            for author in header['author']:
                if ('firstname' in author.keys()) and ('surname' in author.keys()) and ('affiliation' in author.keys()):
                    auth=author['firstname'].encode("UTF-8")+' '+author['surname'].encode("UTF-8")
                    affil=(str(author['affiliation']).replace("aff","")).encode("UTF-8")
                    affil="^,^".join(["^"+a+"^" for a in (''.join(affil.split())).split(',')])
                    if 'corref' in author.keys():
                        affil=affil+"*"
                        if 'email' in author.keys():
                            tc=author['email'].encode("UTF-8")
                        else:
                            tc="missing email"
                        if not email_str:
                            email_str = tc
                        else:
                            email_str = ', '.join([email_str,tc])

                    auth = auth + affil
                    auth=" ".join(auth.split())
                    if not tmp:
                        tmp=auth
                    else:
                        tmp=', '.join([tmp,auth])
        else:
            tmp="Missing Authors"
        outfd.write(tmp+"\n")
        outfd.write("\n\n")

        # add in the affiliations
        tmp=''
        if 'affiliations' in header.keys():
            for aff in header['affiliations']:
                if 'id' in aff.keys():
                    atmp='^'+(str(aff['id']).encode("UTF-8")).replace('aff','')+'^'
                    if 'orgname' in aff.keys():
                        atmp=atmp+aff['orgname'].encode("UTF-8")
                    if 'city' in aff.keys():
                        atmp=atmp+', '+aff['city'].encode("UTF-8")
                    if 'state' in aff.keys():
                        atmp=atmp+', '+aff['state'].encode("UTF-8")
                    if 'country' in aff.keys():
                        atmp=atmp+', '+aff['country'].encode("UTF-8")
                else:
                    tmp="Missing Org"
                if not tmp:
                    tmp=atmp
                else:
                    tmp='\n\n'.join([tmp,atmp])
            outfd.write(tmp+"\n\n")

        if email_str:
            outfd.write("*Email: "+email_str+"\n\n\n\n")

        if body:
            out_body_text = replace_latex(body,citations,labels,os.path.dirname(args.input))
            outfd.write('\n'.join(out_body_text))

        outfd.write("\n\n")
        outfd.write("###Availability of Supporting Data\n")
        outfd.write("More information about this project can be found at: %s\n\n"%(header['url']))

        outfd.write("###Competing interests\n")
        outfd.write(header['coi']+'\n\n')

        outfd.write("###Author's contributions\n")
        outfd.write(header['contrib']+'\n\n')

        outfd.write("###Acknowledgements\n")
        outfd.write(header['acknow']+'\n\n')

        outfd.write("###References\n\n\n")

        import bibtexparser
        with open(os.path.join(os.path.dirname(args.input),header['bibliography']+".bib")) as bibtex_file:
            bibtex_str = bibtex_file.read()

        bib_database = bibtexparser.loads(bibtex_str)

        cnt=1
        for c in citations:
            if 'misc' in bib_database.entries_dict[c]['ENTRYTYPE']:
                authors=",".join([(((a.rstrip()).replace(". ","")).replace(",","")).replace(".","") for a in bib_database.entries_dict[c]['author'].split("and")])
                bib_str = "%d. "%(cnt)
                bib_str = bib_str + authors + ". "
                bib_str = bib_str + bib_database.entries_dict[c]['title'] + ". "
                bib_str = bib_str + bib_database.entries_dict[c]['publisher'] + "; "
                bib_str = bib_str + bib_database.entries_dict[c]['year'] + ". "
                try:
                    bib_str =  bib_str + "doi:" + bib_database.entries_dict[c]['doi'] + "."
                except:
                    bib_str = bib_str + "."
                bib_str=((bib_str.replace("{","")).replace("}","")).replace("--","-") + "\n"
            elif 'incollection' in bib_database.entries_dict[c]['ENTRYTYPE']:
                authors=",".join([(((a.rstrip()).replace(". ","")).replace(",","")).replace(".","") for a in bib_database.entries_dict[c]['author'].split("and")])
                editors=",".join([(((a.rstrip()).replace(". ","")).replace(",","")).replace(".","") for a in bib_database.entries_dict[c]['editor'].split("and")])
                bib_str = "%d. "%(cnt)
                bib_str = bib_str + authors + ". "
                bib_str = bib_str + bib_database.entries_dict[c]['title'] + ". "
                bib_str = bib_str + "In: " + editors + ", editors." + bib_database.entries_dict[c]['booktitle'] + ". "
                bib_str = bib_str + bib_database.entries_dict[c]['address'] + ": "+ bib_database.entries_dict[c]['publisher'] + "; "
                bib_str = bib_str + bib_database.entries_dict[c]['year'] + ". "
                try:
                    bib_str =  bib_str + "p. " + bib_database.entries_dict[c]['pages'] + "."
                except:
                    bib_str = bib_str + "."
                bib_str=((bib_str.replace("{","")).replace("}","")).replace("--","-") + "\n"
            elif 'article' in bib_database.entries_dict[c]['ENTRYTYPE']:
                authors=",".join([(((a.rstrip()).replace(". ","")).replace(",","")).replace(".","") for a in bib_database.entries_dict[c]['author'].split("and")])
                bib_str = "%d. "%(cnt)
                bib_str = bib_str + authors + ". "
                bib_str = bib_str + bib_database.entries_dict[c]['title'] + ". "
                bib_str = bib_str + bib_database.entries_dict[c]['journal'].replace(".","") + ". "
                bib_str = bib_str + bib_database.entries_dict[c]['year'] + "; "
                bib_str = bib_str + bib_database.entries_dict[c]['volume'] 
                try:
                    bib_str =  bib_str + ": " + bib_database.entries_dict[c]['pages'] + "."
                except:
                    bib_str = bib_str + "."
                bib_str=((bib_str.replace("{","")).replace("}","")).replace("--","-") + "\n"
            outfd.write(bib_str)
            cnt=cnt+1

