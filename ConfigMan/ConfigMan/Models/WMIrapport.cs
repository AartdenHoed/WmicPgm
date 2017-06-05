using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Serialization;
using System.Web;

namespace ConfigMan.Models
{
    [DataContract]
    public class WMIrapport
    {
        [DataMember]
        public string ReportedByNode;
        [DataMember]
        public List<Installation> HighestReleaseList;
        [DataMember]
        public List<ReportedComputer> ComputerList;
    }
}