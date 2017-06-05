using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Serialization;
using System.Web;

namespace ConfigMan.Models
{
    [DataContract]
    public class ReportedComputer
    {
        [DataMember]
        public Computer ComputerItem;
        [DataMember]
        public DateTime MeasureDate;
        [DataMember]
        public List<Installation> Inventory;
    }
}