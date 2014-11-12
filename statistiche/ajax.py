from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax
from statistiche.models import *
from persone.models import *
from statistiche.views import *
from dajaxice.utils import deserialize_form
from django.template.loader import render_to_string
from django.template import Context, Template

@dajaxice_register
def aggiorna_statistiche(request,da,al,mansioni,gruppi):
        dajax=Dajax()
        elenco_mansioni=Mansione.objects.filter(id__in=mansioni.rsplit('_'))
        senza_gruppo=False
        #import pdb; pdb.set_trace()
        if "all_" in gruppi:
                senza_gruppo=True
                gruppi=gruppi.replace("all_","")
        if "all" in gruppi:
                senza_gruppo=True
                gruppi=gruppi.replace("all","")
        if gruppi != "":
                elenco_gruppi=Gruppo.objects.filter(id__in=gruppi.rsplit('_'))
        else:
                elenco_gruppi=Gruppo.objects.all()

        data_da=datetime.date(datetime.datetime.today().year,1,1)
        data_al=datetime.datetime.now().date()
        if (da=="0"):
                elenco_mansioni=Mansione.objects.all()
                elenco_gruppi=Gruppo.objects.all()
        elif (da!="" and al!=""):
                data_da=datetime.datetime.strptime(da, "%d/%m/%Y").date()
                data_al=datetime.datetime.strptime(al, "%d/%m/%Y").date()
        tot_turni, tot_punti, tot_turni_dipendenti, tot_punti_dipendenti = statistiche_intervallo(request,data_da,data_al,elenco_mansioni,elenco_gruppi,senza_gruppo)
        html_statistiche = render_to_string( 'statistiche/statistiche.html', { 'tot_turni': tot_turni,
                'tot_punti': tot_punti,
                'tot_punti_dipendenti':tot_punti_dipendenti,
                'tot_turni_dipendenti':tot_turni_dipendenti,
                'get_distingui_dipendenti':getattr(settings, 'GET_DISTINGUI_DIPENDENTI', False),
                'request':request } )
        dajax.assign('div #stat', 'innerHTML', html_statistiche)
        dajax.script("$('#loading').addClass('hidden');")
        return dajax.json()

@dajaxice_register
def dettaglio_turni(request,da,al,mansioni,id):
	dajax=Dajax()
	elenco_mansioni=Mansione.objects.all().filter(id__in=mansioni.rsplit('_')).exclude(escludi_stat=True)
	data_da=datetime.date(datetime.datetime.today().year,1,1)
	data_al=datetime.datetime.now().date()
	if (da=="0"):
			elenco_mansioni=Mansione.objects.exclude(escludi_stat=True)
	elif (da!="" and al!=""):
			data_da=datetime.datetime.strptime(da, "%d/%m/%Y").date()
			data_al=datetime.datetime.strptime(al, "%d/%m/%Y").date()
	mansioni=elenco_mansioni.filter(mansione_disponibilita__persona=id,mansione_disponibilita__tipo="Disponibile",mansione_disponibilita__turno__inizio__gte=data_da, mansione_disponibilita__turno__fine__lte=data_al,).annotate(parziale=Count('id'))
	html_dettagli = render_to_string( 'statistiche/dettagli_mansioni.html', { 'mansioni': mansioni} )
	dajax.assign('div #dettagli-'+str(id), 'innerHTML', html_dettagli)
	return dajax.json()

@dajaxice_register
def statistiche_generali(request,da,al,):
	dajax=Dajax()
	data_da=datetime.date(datetime.datetime.today().year,1,1)
	data_al=datetime.datetime.now().date()
	if (da!="" and al!=""):
		data_da=datetime.datetime.strptime(da, "%d/%m/%Y").date()
		data_al=datetime.datetime.strptime(al, "%d/%m/%Y").date()
	stato_turno=Turno.objects.filter(inizio__gte=data_da, fine__lte=data_al,).values('coperto').annotate(dcount=Count('coperto'))
	tipi_turno=Turno.objects.filter(inizio__gte=data_da, fine__lte=data_al,).values('tipo','tipo__identificativo').annotate(dcount=Count('tipo'))
	html_generali = render_to_string( 'statistiche/generali.html', { 'tipi_turno': tipi_turno, 'stato_turno': stato_turno} )
	dajax.assign('div #tabs-generali', 'innerHTML', html_generali)
	#import pdb; pdb.set_trace()
	return dajax.json()