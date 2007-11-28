  
#
#molTypes = {}
#seq_length = {}
#for entry in pdbList:
#    try:
#        inputFN  = os.path.join(linkDir,entry,entry+'_full.str')
#        headFN = os.path.join(tmpDir,       entry+'_head.str')
#        f = File()
#        saveFrameRegExList = [r"^save_.*constraints", r"^save_conformer"]
#        f.getHeader(saveFrameRegExList, inputFN, headFN)
#        f.filename = headFN
#        f.read()
#        os.unlink( f.filename )
#        molTypesPerEntry = {}
#        molTypes[entry] = molTypesPerEntry
#        seq_lengthPerEntry = {}
#        seq_length[entry] = seq_lengthPerEntry
#        sfList = f.getSaveFrames( category = 'entity')
#        for node in sfList:
#            tT = node.tagtables[0]
#    #        print tT
#            typeIdx = tT.tagnames.index('_Entity.Type')
#    #        print typeIdx
#            type = tT.tagvalues[typeIdx][0]
#            poltype = ''
#            if '_Entity.Pol_type' in tT.tagnames:
#                poltypeIdx = tT.tagnames.index('_Entity.Pol_type')
#        #        print poltypeIdx            
#                poltype = tT.tagvalues[poltypeIdx][0]
#                
#    #        print "type", type, ", and poltype", poltype
#            key = type +'/' + poltype
#            if molTypesPerEntry.has_key(key):
#                molTypesPerEntry[key] += 1
#            else:
#                molTypesPerEntry[key] = 1  
#                
#            lengthIdx = -1
#            if '_Entity.Seq_length' in tT.tagnames:
#                lengthIdx = tT.tagnames.index('_Entity.Seq_length')
#            if lengthIdx>=0:
#                length = string.atoi(tT.tagvalues[lengthIdx][0])
#            else:
#                length = 0
#                
#            if seq_lengthPerEntry.has_key(key):
#                seq_lengthPerEntry[key] += length
#            else:
#                seq_lengthPerEntry[key] = length
#
#                         
#        for key in molTypes[entry].keys():
#            str = entry+","+key+','+`molTypes[entry][key]`+','+`seq_length[entry][key]`
#            print str
#    except KeyboardInterrupt:
#        print "ERROR: Caught KeyboardInterrupt will exit(1)"
#        os._exit(1)
#    except Exception, info:
#        print "Skipping entry: ", entry, info
#                
#print molTypes         
#output = open('S:\\jurgen\\CloneWars\\DOCR1000\\Paper\\moltypes.csv','w')
#for entry in molTypes.keys().sort():
#    for key in molTypes[entry].keys().sort():
#        str = entry+","+key+','+`molTypes[entry][key]`+','+`seq_length[entry][key]`+'\n'
#        output.write(str)
#            
#                
